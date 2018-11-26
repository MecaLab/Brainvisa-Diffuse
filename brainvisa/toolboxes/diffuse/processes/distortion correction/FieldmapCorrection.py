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

import numpy
from copy import copy
from brainvisa.processes import *
from brainvisa.diffuse import BrainExtraction
from soma.wip.application.api import Application
from brainvisa.registration import getTransformationManager
from brainvisa.tools import aimsGlobals

name = 'Fieldmap-based correction'
userLevel = 0

##Susceptibility induced distortion correction using FSL-FUGUE
##Requires a reconstructed fieldmap in rad/s and a magnitude image
##(see http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FUGUE/Guide for reconstruction of fieldmap image)
## echo-spacing (in sec)

signature = Signature(
  'data_are_eddy_current_corrected', Boolean(),
  'dwi_data', ReadDiskItem( 'Raw Denoised Diffusion MR', 'Aims readable volume formats' ),
  'bvals', ReadDiskItem( 'Raw B Values', 'Text file' ),
  'fieldmap', ReadDiskItem( 'Fieldmap Phase', 'Aims readable volume formats' ),
  'magnitude', ReadDiskItem( 'Fieldmap Magnitude', 'Aims readable volume formats' ),

  'echo_spacing', Number(),
  'phase_encoding_direction', Choice( "AP", "PA", "LR", "RL" ),
  'fieldmap_smoothing', Number(),
  'brain_extraction_factor', Number(),

  'dwi_unwarped', WriteDiskItem( 'Unwarped DW Diffusion MR', 'gz compressed NIFTI-1 image' ),
  'fieldmap_brain', WriteDiskItem( 'Fieldmap Phase Brain', 'gz compressed NIFTI-1 image' ),
  'magnitude_brain', WriteDiskItem( 'Fieldmap Magnitude Brain', 'gz compressed NIFTI-1 image' ),
  'magnitude_brain_mask', WriteDiskItem( 'Fieldmap Magnitude Mask', 'gz compressed NIFTI-1 image' ),
  'magnitude_warped', WriteDiskItem( 'Fieldmap Magnitude Warped', 'gz compressed NIFTI-1 image' ),
  'magnitude_warped_to_dwi', WriteDiskItem( 'Fieldmap Magnitude Warped Reg', 'gz compressed NIFTI-1 image' ),
  'fieldmap_to_dwi_mat', WriteDiskItem( 'Fieldmap to DW Mat', 'Matlab file' ),
  'fieldmap_to_dwi', WriteDiskItem( 'Fieldmap Phase Reg', 'gz compressed NIFTI-1 image' ),
  # 'magnitude_warped_to_dwi_brain', WriteDiskItem( 'Fieldmap Magnitude Warped Brain Reg', 'gz compressed NIFTI-1 image' ),
  # 'magnitude_warped_to_dwi_brain_mask', WriteDiskItem( 'Fieldmap Magnitude Warped Mask Reg', 'gz compressed NIFTI-1 image' ),
)

def switchCorrection( self, data_are_eddy_current_corrected):
  if self.data_are_eddy_current_corrected:
    dwi_type = 'EC corrected DW Diffusion MR'
  else:
    dwi_type = 'Raw Denoised Diffusion MR'
  if dwi_type == self.signature[ 'dwi_data' ].type.name:
    return
  signature = copy( self.signature )
  signature[ 'dwi_data' ] = ReadDiskItem( dwi_type, 'Aims readable volume formats' )
  self.changeSignature( signature )

def linkOutput(self, proc, dummy):
    required = {}
    required['center'] = self.dwi_data.get('center')
    required['subject'] = self.dwi_data.get('subject')
    required['acquisition'] = self.dwi_data.get('acquisition')
    return self.signature['dwi_unwarped'].findValue(self.dwi_data, requiredAttributes=required)

def initialization( self ):
    self.data_are_eddy_current_corrected = True
    self.addLink( None, 'data_are_eddy_current_corrected', self.switchCorrection )
    self.linkParameters( 'bvals', 'dwi_data' )
    self.linkParameters( 'fieldmap', 'dwi_data' )
    self.linkParameters( 'magnitude', 'dwi_data' )
    self.brain_extraction_factor = 0.3
    self.fieldmap_smoothing = 0.5
    self.linkParameters('dwi_unwarped', 'dwi_data', self.linkOutput)
    self.linkParameters( 'fieldmap_brain', 'dwi_unwarped' )
    self.linkParameters( 'magnitude_brain', 'dwi_unwarped' )
    self.linkParameters( 'magnitude_brain_mask', 'dwi_unwarped' )
    self.linkParameters( 'magnitude_warped', 'dwi_unwarped' )
    self.linkParameters( 'magnitude_warped_to_dwi', 'dwi_unwarped' )
    self.linkParameters( 'fieldmap_to_dwi_mat', 'dwi_unwarped' )
    self.linkParameters( 'fieldmap_to_dwi', 'dwi_unwarped' )
    # self.linkParameters( 'magnitude_warped_to_dwi_brain', 'dwi_unwarped' )
    # self.linkParameters( 'magnitude_warped_to_dwi_brain_mask', 'dwi_unwarped' )

def execution( self, context ):

    context.write('Susceptibility induced distortion correction using Fieldmap... [~1mn]')
  
    context.write('- Identification of first b0 volume')
    img = aims.read(self.dwi_data.fullPath())
    dwi_data = img.arraydata()
    bvals = numpy.loadtxt(self.bvals.fullPath())
    b0_index = numpy.where(bvals < 100)[0] ## bvals==0 not possible when bvalues take values +-5 or +-10
    b0 = dwi_data[b0_index[0], :, :, :]
    b0_vol = aims.Volume(b0)
    b0_vol.copyHeaderFrom(img.header())
    b0_tmp = context.temporary( 'NIFTI-1 image' )
    aims.write(b0_vol, b0_tmp.fullPath())
    
    configuration = Application().configuration
    FSL_directory = os.path.dirname(self.fieldmap_brain.fullPath())

    PE_list = ["AP", "PA", "LR", "RL"]
    dir_list = ["y-","y","x-","x"]
    warping_direction = dir_list[PE_list.index(self.phase_encoding_direction)]

    context.write('- Brain extraction of magnitude image')
    BrainExtraction.defaultBrainExtraction(self.magnitude.fullPath(), self.magnitude_brain.fullPath(), f=str(self.brain_extraction_factor))
    # cmd = [ configuration.FSL.fsl_commands_prefix + 'fslmaths', self.fieldmap.fullPath(), '-mas', self.magnitude_brain.fullPath(), self.fieldmap_brain.fullPath() ]
    # context.system( *cmd )

    # unmask the fieldmap (necessary to avoid edge effects)
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fslmaths', self.magnitude_brain.fullPath(), '-bin', self.magnitude_brain_mask.fullPath() ] #
    context.system( *cmd ) #
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fugue', '--loadfmap=' + self.fieldmap.fullPath(), '--mask=' + self.magnitude_brain_mask.fullPath(), '--unmaskfmap', '--savefmap=' + self.fieldmap_brain.fullPath(), '--unwarpdir=' + warping_direction ] #
    context.system( *cmd ) #

    context.write('- Fieldmap smoothing')
    cmd = [configuration.FSL.fsl_commands_prefix + 'fugue', '--loadfmap=' + self.fieldmap_brain.fullPath(), '--despike', '--smooth3=' + str(self.fieldmap_smoothing), '--savefmap=' + self.fieldmap_brain.fullPath()]
    context.system(*cmd)

    context.write('- Magnitude image warping using fieldmap')
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fugue', '-v', '-i', self.magnitude_brain.fullPath(), '--dwell=' + str(self.echo_spacing), '--unwarpdir=' + warping_direction,
            '--loadfmap=' + self.fieldmap_brain.fullPath(), '-w', self.magnitude_warped.fullPath()]
    context.system( *cmd )

    
    context.write('- Registration of fieldmap into diffusion space')
    cmd1 = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-dof', '12', '-in', self.magnitude_warped.fullPath(), '-ref', b0_tmp.fullPath(), '-out', self.magnitude_warped_to_dwi.fullPath(), '-omat', self.fieldmap_to_dwi_mat.fullPath() ]
    cmd2 = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-dof', '12', '-in', self.fieldmap_brain.fullPath(), '-ref', b0_tmp.fullPath(), '-applyxfm', '-init', self.fieldmap_to_dwi_mat.fullPath(), '-out', self.fieldmap_to_dwi.fullPath() ]
    context.system( *cmd1)
    context.system( *cmd2)
    transformManager = getTransformationManager()
    transformManager.copyReferential( self.dwi_data, self.magnitude_warped_to_dwi )
    transformManager.copyReferential( self.dwi_data, self.fieldmap_to_dwi )

    context.write('- Unwarping of dwi image using fieldmap')
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fugue', '-v', '-i', self.dwi_data.fullPath(), '--dwell=' + str(self.echo_spacing), '--unwarpdir=' + warping_direction,
            '--loadfmap=' + self.fieldmap_to_dwi.fullPath(), '-u', self.dwi_unwarped.fullPath(), '--icorr', '--saveshift=' + FSL_directory + '/pixel_shift.nii.gz' ] #'--mask=' + self.magnitude_warped_to_dwi_brain_mask.fullPath(), '--smooth3='  + str(self.fieldmap_smoothing),
    context.system( *cmd)
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fslmaths', self.dwi_unwarped.fullPath(), '-abs', self.dwi_unwarped.fullPath() ]
    context.system( *cmd)
    
    transformManager.copyReferential( self.dwi_data, self.dwi_unwarped )
    
    context.write('Finished')
