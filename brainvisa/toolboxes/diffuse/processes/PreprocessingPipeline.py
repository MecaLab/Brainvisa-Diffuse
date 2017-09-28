#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from brainvisa.processes import *
from copy import copy

name = 'Diffusion Preprocessing Pipeline'
userLevel = 0

signature = Signature(
    'dwi_data', ReadDiskItem( 'Raw Denoised Diffusion MR', 'Aims readable volume formats' ),
    'T1_volume', ReadDiskItem( 'T1 MRI Bias Corrected', 'Aims readable volume formats' ),
    'additional_acquisition', Choice("None", "Fieldmap", "Blip-reversed images"),
    
    'phase_encoding_direction', Choice( "AP", "PA", "LR", "RL" ),
    'entire_sphere_sampling', Boolean(),
    'multi_shell', Boolean(),
    'echo_spacing', Number(),
    'readout_time', Number(),
    
    'dwi_eddy_corrected', WriteDiskItem( 'EC corrected DW Diffusion MR', 'gz compressed NIFTI-1 image' ),
    'dwi_unwarped', WriteDiskItem( 'Unwarped DW Diffusion MR', 'gz compressed NIFTI-1 image' ),
    'b0_volume', WriteDiskItem( 'B0 Volume', 'gz compressed NIFTI-1 image' ),
    'b0_brain', WriteDiskItem( 'B0 Volume Brain', 'gz compressed NIFTI-1 image' ),
    'T1_to_b0', WriteDiskItem('T1 MRI to DW Diffusion MR', 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_registration_method', Choice("niftyreg", "fnirt"),
)

def switchSignature( self, additional_acquisition ):
    signature = copy( self.signature )
    self.setHidden('echo_spacing')
    self.setHidden('phase_encoding_direction')
    self.setHidden('readout_time')
    self.setOptional('echo_spacing')
    self.setOptional('readout_time')
    if self.additional_acquisition == "Fieldmap":
        self.setEnable('phase_encoding_direction')
        self.setEnable('echo_spacing')
        self.setOptional('readout_time')
    elif self.additional_acquisition == "Blip-reversed images":
        self.setEnable('phase_encoding_direction')
        self.setEnable('readout_time')
        self.setOptional('echo_spacing')
    self.changeSignature( signature )

def switchExtractB0Input( self, additional_acquisition ):
    eNode = self.executionNode()
    signature =  copy( eNode.ExtractB0.signature )
    linkTo = 'dwi_eddy_corrected'
    if self.additional_acquisition == "None":
        dwi_type = 'EC Corrected DW Diffusion MR'
        linkTo = 'dwi_eddy_corrected'
    if self.additional_acquisition in ["Fieldmap", "Blip-reversed images"]:
        dwi_type = 'Unwarped DW Diffusion MR'
        linkTo = 'dwi_unwarped'
    if dwi_type == self.signature['dwi_data'].type.name:
        return
    signature['dwi_data'] = ReadDiskItem( dwi_type, 'Aims readable volume formats' )
    eNode.ExtractB0.changeSignature( signature )
    eNode.addLink( 'ExtractB0.dwi_data', linkTo, destDefaultUpdate=False )
    val = getattr( eNode, 'dwi_eddy_corrected' )
    eNode._parameterHasChanged( 'dwi_eddy_corrected', val)


def linkOutput(self, proc, dummy):
    required = {}
    required['center'] = self.dwi_data.get('center')
    required['subject'] = self.dwi_data.get('subject')
    required['acquisition'] = self.dwi_data.get('acquisition')
    return self.signature['dwi_unwarped'].findValue(self.dwi_data, requiredAttributes=required)


def initialization( self ):
    self.entire_sphere_sampling = False
    self.multi_shell = False
    self.addLink( None, 'additional_acquisition', self.switchSignature)
    self.linkParameters('dwi_eddy_corrected', 'dwi_data', self.linkOutput)
    self.addLink( 'dwi_unwarped', 'dwi_eddy_corrected' )
    self.addLink( 'b0_volume', 'dwi_unwarped' )
    self.setOptional('T1_volume')

    def t1Processing(enabled, names, parameterized):
        eNode = parameterized[0].executionNode()
        if not self.T1_volume:
            eNode.T1Reg.setSelected(False)
            eNode.BrainExtraction.setSelected(False)
            eNode.MeshRegistrationLeft.setSelected(False)
            eNode.MeshRegistrationRight.setSelected(False)
        else:
            eNode.T1Reg.setSelected(True)
            eNode.BrainExtraction.setSelected(True)
            eNode.MeshRegistrationLeft.setSelected(True)
            eNode.MeshRegistrationRight.setSelected(True)

    def switchEddy(enabled, names, parameterized):
        signature = copy( self.signature )
        eNode = parameterized[0].executionNode()
        if self.entire_sphere_sampling:
            eNode.DistortionCorrection.m1.Eddy.FSLeddy.setSelected(True)
            self.setEnable('readout_time')
            self.setEnable('phase_encoding_direction')
        else:
            eNode.DistortionCorrection.m1.Eddy.AffineRegistration.setSelected(True)
            self.setHidden('readout_time')
            if self.additional_acquisition == "None":
                self.setHidden('phase_encoding_direction')
        self.changeSignature( signature )
        
    def switchCorrection(enabled, names, parameterized):
        eNode = parameterized[0].executionNode()
        if self.additional_acquisition in ["None", "Fieldmap"]:
            eNode.DistortionCorrection.m1.setSelected(True)
            eNode.DistortionCorrection.m2.BlipReversed.setSelected(False)
            if self.additional_acquisition == "None":
                eNode.DistortionCorrection.m1.Fieldmap.setSelected(False)
            elif self.additional_acquisition == "Fieldmap":
                eNode.DistortionCorrection.m1.Fieldmap.setSelected(True)
        else:
            eNode.DistortionCorrection.m2.setSelected(True)
            eNode.DistortionCorrection.m2.BlipReversed.setSelected(True)
            eNode.DistortionCorrection.m1.Fieldmap.setSelected(False)

    def switchRegistration(enabled, names, parameterized):
        eNode = parameterized[0].executionNode()
        if self.T1_to_b0_registration_method == 'niftyreg':
            eNode.T1Reg.NIFTYREG.setSelected(True)
        elif self.T1_to_b0_registration_method == 'fnirt':
            eNode.T1Reg.FNIRT.setSelected(True)

    eNode = SerialExecutionNode( self.name, parameterized = self )
    
    eNode.addChild( 'GradientOrientation', ProcessExecutionNode( 'CorrectGradientOrientation', optional = 1 ))
    
    distortionNode = SelectionExecutionNode( 'Distortion correction', optional = 1, selected = 1, expandedInGui = 1 )
    eNode.addChild( 'DistortionCorrection', distortionNode )
    distortionNode1 = SerialExecutionNode( 'Method 1', selected = 1, expandedInGui = 1 )
    distortionNode2 = SerialExecutionNode( 'Method 2', selected = 0, expandedInGui = 1 )
    distortionNode.addChild( 'm1', distortionNode1 )
    distortionNode.addChild( 'm2', distortionNode2 )
    eddyNode = SelectionExecutionNode( 'Eddy-current correction', optional = 1, selected = 1, expandedInGui = 1 )
    distortionNode1.addChild( 'Eddy', eddyNode)
    eddyNode.addChild( 'AffineRegistration', ProcessExecutionNode( 'EddyCurrentCorrectionECCAR', optional = 1, selected=True, altname='Affine Registration' ))
    eddyNode.addChild( 'FSLeddy', ProcessExecutionNode( 'EddyCurrentCorrectionEDDY', optional = 1, selected=False, altname='FSL-eddy' ))
    distortionNode1.addChild( 'Fieldmap', ProcessExecutionNode( 'FieldmapCorrection', optional = 1 ))
    distortionNode2.addChild( 'BlipReversed', ProcessExecutionNode( 'BlipReversedCorrection', optional = 1 ))

    eNode.addChild('PreprocessingCleanUp', ProcessExecutionNode('PreprocessingCleanup', optional=1, selected=False))
    eNode.addLink('PreprocessingCleanUp.Preprocessing_directory', 'dwi_eddy_corrected')

    eNode.addChild( 'ExtractB0', ProcessExecutionNode( 'NoDiffusionVolumeExtraction', optional = 1 ))
    regNode = SelectionExecutionNode('Diffusion to T1 registration', optional=1, selected=0, expandedInGui=1)
    eNode.addChild( 'T1Reg', regNode)
    regNode.addChild( 'NIFTYREG', ProcessExecutionNode('DiffusionToT1_niftyreg', optional = 1, selected=False, altname='Non-linear registration using NIFTYREG'))
    regNode.addChild('FNIRT', ProcessExecutionNode('DiffusionToT1_nonlinear', optional=1, selected=False, altname='Non-linear registration using FNIRT'))
    eNode.addChild( 'BrainExtraction', ProcessExecutionNode( 'BrainExtractionUsingT1', optional = 1, selected=False, altname='Brain Extraction' ))
    eNode.addChild( 'MeshRegistrationLeft', ProcessExecutionNode('ApplyT1ToDiffusionMesh', optional=1, selected=False, altname='Mesh registration Left'))
    eNode.addChild( 'MeshRegistrationRight', ProcessExecutionNode('ApplyT1ToDiffusionMesh', optional=1, selected=False, altname='Mesh registration Right'))

    eNode.addLink(None, 'additional_acquisition', switchCorrection)
    eNode.addLink( None, 'entire_sphere_sampling', switchEddy )
    eNode.addLink(None, 'T1_volume', t1Processing)
    eNode.addLink(None, 'T1_to_b0_registration_method', switchRegistration)

    eNode.addLink( 'GradientOrientation.dwi_data', 'dwi_data' )
    eNode.GradientOrientation.visual_check = False

    eNode.addLink( 'DistortionCorrection.m1.Eddy.AffineRegistration.dwi_data', 'dwi_data' )
    eNode.DistortionCorrection.m1.Eddy.AffineRegistration.removeLink( 'bvecs', 'dwi_data' )
    eNode.addLink( 'DistortionCorrection.m1.Eddy.AffineRegistration.bvecs', 'GradientOrientation.reoriented_bvecs' )
    eNode.DistortionCorrection.m1.Eddy.AffineRegistration.removeLink( 'dwi_eddy_corrected', 'dwi_data' )
    eNode.addLink( 'DistortionCorrection.m1.Eddy.AffineRegistration.dwi_eddy_corrected', 'dwi_eddy_corrected' )

    eNode.addLink( 'DistortionCorrection.m1.Eddy.FSLeddy.dwi_data', 'dwi_data' )
    eNode.DistortionCorrection.m1.Eddy.FSLeddy.removeLink( 'bvecs', 'dwi_data' )
    eNode.addLink( 'DistortionCorrection.m1.Eddy.FSLeddy.bvecs', 'GradientOrientation.reoriented_bvecs' )
    eNode.addLink( 'DistortionCorrection.m1.Eddy.FSLeddy.readout_time', 'readout_time' )
    eNode.addLink('DistortionCorrection.m1.Eddy.FSLeddy.entire_sphere_sampling', 'entire_sphere_sampling')
    eNode.addLink('DistortionCorrection.m1.Eddy.FSLeddy.multi_shell', 'multi_shell')
    eNode.addLink( 'DistortionCorrection.m1.Eddy.FSLeddy.phase_encoding_direction', 'phase_encoding_direction' )
    eNode.DistortionCorrection.m1.Eddy.FSLeddy.removeLink( 'dwi_eddy_corrected', 'dwi_data' )
    eNode.addLink( 'DistortionCorrection.m1.Eddy.FSLeddy.dwi_eddy_corrected', 'dwi_eddy_corrected' )
        
    eNode.addLink( 'DistortionCorrection.m1.Fieldmap.dwi_data', 'dwi_eddy_corrected' )
    eNode.addLink( 'DistortionCorrection.m1.Fieldmap.echo_spacing', 'echo_spacing' )
    eNode.addLink( 'DistortionCorrection.m1.Fieldmap.phase_encoding_direction', 'phase_encoding_direction' )
    eNode.DistortionCorrection.m1.Fieldmap.removeLink('dwi_unwarped', 'dwi_data' )
    eNode.addLink( 'DistortionCorrection.m1.Fieldmap.dwi_unwarped', 'dwi_unwarped' )
    
    eNode.addLink( 'DistortionCorrection.m2.BlipReversed.dwi_data', 'dwi_data' )
    eNode.DistortionCorrection.m2.BlipReversed.removeLink( 'bvecs', 'dwi_data' )
    eNode.addLink( 'DistortionCorrection.m2.BlipReversed.bvecs', 'GradientOrientation.reoriented_bvecs' )
    eNode.addLink( 'DistortionCorrection.m2.BlipReversed.phase_encoding_direction', 'phase_encoding_direction' )
    eNode.addLink( 'DistortionCorrection.m2.BlipReversed.entire_sphere_sampling', 'entire_sphere_sampling' )
    eNode.addLink( 'DistortionCorrection.m2.BlipReversed.multi_shell', 'multi_shell' )
    eNode.addLink( 'DistortionCorrection.m2.BlipReversed.readout_time', 'readout_time' )
    eNode.DistortionCorrection.m2.BlipReversed.removeLink( 'dwi_unwarped', 'dwi_data' )
    eNode.addLink( 'DistortionCorrection.m2.BlipReversed.dwi_unwarped', 'dwi_unwarped' )

    eNode.addLink( None, 'additional_acquisition', self.switchExtractB0Input )
    eNode.ExtractB0.removeLink( 'b0_volume', 'dwi_data' )
    eNode.addLink( 'ExtractB0.b0_volume', 'b0_volume' )

    eNode.addLink( 'T1Reg.NIFTYREG.T1_volume', 'T1_volume' )
    eNode.addLink( 'T1Reg.NIFTYREG.b0_volume', 'ExtractB0.b0_volume' )
    eNode.T1Reg.NIFTYREG.removeLink( 'dwi_data', 'b0_volume' )
    eNode.addLink( 'T1Reg.NIFTYREG.dwi_data', 'ExtractB0.dwi_data' )
    eNode.addDoubleLink( 'T1Reg.NIFTYREG.T1_to_b0', 'T1_to_b0' )

    eNode.addLink('T1Reg.FNIRT.T1_volume', 'T1_volume')
    eNode.addLink('T1Reg.FNIRT.b0_volume', 'ExtractB0.b0_volume')
    eNode.T1Reg.FNIRT.removeLink('dwi_data', 'b0_volume')
    eNode.addLink('T1Reg.FNIRT.dwi_data', 'ExtractB0.dwi_data')
    eNode.addDoubleLink('T1Reg.FNIRT.T1_to_b0', 'T1_to_b0')
    
    eNode.addLink( 'BrainExtraction.b0_volume', 'ExtractB0.b0_volume' )
    eNode.BrainExtraction.removeLink( 'T1_to_b0_mask', 'b0_volume' )
    eNode.addLink( 'BrainExtraction.T1_to_b0_mask', 'T1Reg.FNIRT.T1_to_b0_mask' )
    eNode.addDoubleLink( 'BrainExtraction.b0_brain', 'b0_brain' )

    eNode.addLink( 'MeshRegistrationLeft.b0_volume', 'ExtractB0.b0_volume' )
    eNode.addLink('MeshRegistrationLeft.T1_volume', 'T1_volume')
    eNode.MeshRegistrationLeft.side = 'left'

    eNode.addLink('MeshRegistrationRight.b0_volume', 'ExtractB0.b0_volume')
    eNode.addLink('MeshRegistrationRight.T1_volume', 'T1_volume')
    eNode.MeshRegistrationRight.side = 'right'

    self.setExecutionNode( eNode )
