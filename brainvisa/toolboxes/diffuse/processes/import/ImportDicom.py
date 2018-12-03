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


def validation():
    from distutils.spawn import find_executable
    mricronx = find_executable( 'dcm2niix' )
    if not mricronx:
       mricron = find_executable('dcm2nii')
       if not mricron:
           raise ValidationError( 'MRICRON dcm2nii(x) program not found' )
    pass

from brainvisa.processes import *
from soma.wip.application.api import Application
from brainvisa.diffuse import DicomToNifti
from distutils.spawn import find_executable
from copy import copy
import os
import glob
import dicom

name = 'Import diffusion data (dicom)'
userLevel = 0
roles = ( 'importer' )



signature=Signature(
  'dwi_directory', ReadDiskItem( 'Directory', 'Directory' ),
  'additional_acquisition', Choice("None", "Fieldmap", "Blip-reversed images"),
  'blip_reversed_directory', ReadDiskItem( 'Directory', 'Directory' ),
  'fieldmap_directory', ReadDiskItem( 'Directory', 'Directory' ),
  'magnitude_directory', ReadDiskItem( 'Directory', 'Directory' ),
  'mricron_program', Choice('dcm2niix', 'dcm2nii'),
  'output_dwi_data', WriteDiskItem( 'Raw Diffusion MR', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),
  'output_bvals', WriteDiskItem( 'Raw B Values', 'Text file' ),
  'output_bvecs', WriteDiskItem( 'Raw B Vectors', 'Text file' ),
  'output_blip_reversed_data', WriteDiskItem( 'Blip Reversed DW Diffusion MR', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),
  'output_fieldmap', WriteDiskItem( 'Fieldmap Phase', 'gz compressed NIFTI-1 image' ),
  'output_magnitude', WriteDiskItem( 'Fieldmap Magnitude', 'gz compressed NIFTI-1 image' ),
)
def switchSignature( self, additional_acquisition ):
    signature = copy( self.signature )
    self.setOptional('blip_reversed_directory')
    self.setOptional('fieldmap_directory')
    self.setOptional('magnitude_directory')
    self.setOptional('output_blip_reversed_data')
    self.setOptional('output_fieldmap')
    self.setOptional('output_magnitude')
    self.setHidden('blip_reversed_directory')
    self.setHidden('fieldmap_directory')
    self.setHidden('magnitude_directory')
    self.setHidden('output_blip_reversed_data')
    self.setHidden('output_fieldmap')
    self.setHidden('output_magnitude')
    if self.additional_acquisition=="Fieldmap":
        self.setEnable('fieldmap_directory')
        self.setEnable('magnitude_directory')
        self.setEnable('output_fieldmap')
        self.setEnable('output_magnitude')
    elif self.additional_acquisition=="Blip-reversed images":
        self.setEnable('blip_reversed_directory')
        self.setEnable('output_blip_reversed_data')
    self.changeSignature( signature )

def initSubject(self, inp):
    value = self.dwi_directory
    if self.dwi_directory is not None:
        value = self.dwi_directory.hierarchyAttributes()
        if value.get("subject", None) is None:
            value["subject"] = os.path.basename(
                self.dwi_directory.fullPath()).partition(".")[0]
    return value

def initialization( self ):
  self.addLink( None, 'additional_acquisition', self.switchSignature )
  self.addLink("output_dwi_data", "dwi_directory", self.initSubject)
  self.signature['output_dwi_data'].browseUserLevel = 3
  self.signature['output_bvals'].browseUserLevel = 3
  self.signature['output_bvecs'].browseUserLevel = 3
  self.signature['output_blip_reversed_data'].browseUserLevel = 3
  self.signature['output_fieldmap'].browseUserLevel = 3
  self.signature['output_magnitude'].browseUserLevel = 3
  self.linkParameters( 'output_bvals', 'output_dwi_data' )
  self.linkParameters( 'output_bvecs', 'output_dwi_data' )
  self.linkParameters( 'output_blip_reversed_data', 'output_dwi_data' )
  self.linkParameters( 'output_fieldmap', 'output_dwi_data' )
  self.linkParameters( 'output_magnitude', 'output_dwi_data' )
  #fix to dcm2niix --> for DICOM this is the best
  self.mricron_program ='dcm2niix'
  
def execution( self, context ):
    configuration = Application().configuration
    tmp_directory = configuration.brainvisa.temporaryDirectory

    # Dicom converter -> to nifti

    #if self.mricron_program=='dcm2niix':
    #    mricron = find_executable('dcm2niix')
       # if not mricron:
            #context.write('MRICRON dcm2nii program not found. Will use dcm2niix instead' )
            #mricron = find_executable('dcm2niix')
            #self.mricron_program = 'dcm2niix'
           # if not mricron:
                #raise RuntimeError(_t_('dcm2nii or dcm2niix executable NOT found !'))

    DicomToNifti.dicom_to_nifti(self.dwi_directory, self.mricron_program, context)
    outputFiles = glob.glob(os.path.join(self.dwi_directory.fullPath(), '*.nii.gz'))
    print outputFiles
    context.system( 'mv', glob.glob(os.path.join(self.dwi_directory.fullPath(), '*.nii.gz'))[0], tmp_directory + '/dwi.nii.gz' ) #data
    context.system( 'mv', glob.glob(os.path.join(self.dwi_directory.fullPath(), '*.bvec'))[0], tmp_directory + '/bvec.txt' ) #data
    context.system( 'mv', glob.glob(os.path.join(self.dwi_directory.fullPath(), '*.bval'))[0], tmp_directory + '/bval.txt' ) #data

    if self.additional_acquisition=="Fieldmap":
        DicomToNifti.dicom_to_nifti(self.fieldmap_directory, self.mricron_program, context)
        context.system( 'mv', glob.glob(os.path.join(self.fieldmap_directory.fullPath(), '*.nii.gz'))[0], tmp_directory + '/phase.nii.gz' ) #_e2phdata
        for f in glob.glob(os.path.join(self.fieldmap_directory.fullPath(), '*.nii.gz')):
            context.system( 'rm', f) #_e2data
        DicomToNifti.dicom_to_nifti(self.magnitude_directory, self.mricron_program, context)
        context.system( 'mv', glob.glob(os.path.join(self.magnitude_directory.fullPath(), '*.nii.gz'))[0], tmp_directory + '/mag.nii.gz' ) #data
        for f in glob.glob(os.path.join(self.magnitude_directory.fullPath(), '*.nii.gz')):
            context.system( 'rm', f) #_e2data

    elif self.additional_acquisition=="Blip-reversed images":
        DicomToNifti.dicom_to_nifti(self.blip_reversed_directory, self.mricron_program, context)
        context.system( 'mv', glob.glob(os.path.join(self.blip_reversed_directory.fullPath(), '*.nii.gz'))[0], tmp_directory + '/blip_reversed.nii.gz' ) #data
        #for f in glob.glob(os.path.join(self.magnitude_directory.fullPath(), '*')):
            #context.system('rm', f)  # _e2data
        
    # Import data
    if self.additional_acquisition=="None":
        context.runProcess( 'Import', dwi_data=tmp_directory + '/dwi.nii.gz', bvals=tmp_directory + '/bval.txt', bvecs=tmp_directory + '/bvec.txt', additional_acquisition=self.additional_acquisition, output_dwi_data=self.output_dwi_data, output_bvals=self.output_bvals, output_bvecs=self.output_bvecs )
    if self.additional_acquisition=="Fieldmap":
        context.runProcess( 'Import', dwi_data=tmp_directory + '/dwi.nii.gz', bvals=tmp_directory + '/bval.txt', bvecs=tmp_directory + '/bvec.txt', additional_acquisition=self.additional_acquisition, output_dwi_data=self.output_dwi_data, output_bvals=self.output_bvals, output_bvecs=self.output_bvecs, fieldmap=tmp_directory + '/phase.nii.gz', magnitude=tmp_directory + '/mag.nii.gz', output_fieldmap=self.output_fieldmap, output_magnitude=self.output_magnitude )
    if self.additional_acquisition=="Blip-reversed images":
        context.runProcess( 'Import', dwi_data=tmp_directory + '/dwi.nii.gz', bvals=tmp_directory + '/bval.txt', bvecs=tmp_directory + '/bvec.txt', additional_acquisition=self.additional_acquisition, output_dwi_data=self.output_dwi_data, output_bvals=self.output_bvals, output_bvecs=self.output_bvecs, blip_reversed_data=tmp_directory + '/blip_reversed.nii.gz', output_blip_reversed_data=self.output_blip_reversed_data )

    # Dicom header info
    files = os.listdir(self.dwi_directory.fullPath())
    file0 = files[0]
    header = dicom.read_file(self.dwi_directory.fullPath() + '/' + file0)
    print header
    manufact = header['0008','0070'].value
    acqMat = header.get('AcquisitionMatrix')
    # acqMat: Dimensions of the acquired frequency /phase data before reconstruction. Multi-valued: frequency rows\frequency columns\phase rows\phase columns
    if acqMat[0]==0 & acqMat[3]==0: # phase-encoding LR/RL
        PE = 'x axis or LR/RL'
        dimx = acqMat[2]
        dimy = acqMat[1]
        Nvox = dimx
    elif acqMat[1]==0 & acqMat[2]==0: # phase-encoding AP/PA
        PE = 'y axis or AP/PA'
        dimx = acqMat[0]
        dimy = acqMat[3]
        Nvox = dimy
    dimz = header['0019','100a'].value
    TR = header.get('RepetitionTime')
    TE = header.get('EchoTime')
    BdWpp = header['0019','1028'].value
    ESeff = 1/(BdWpp*Nvox)
    RT = 1/BdWpp
    context.write('Manufacturer: ' + manufact)
    context.write('TR = ' + str(TR))
    context.write('TE = ' + str(TE))
    context.write('BandwidthPerPixelPhaseEncode (Hz) = ' + str(BdWpp))
    context.write('Effective Echo Spacing (s) = ' + str(ESeff))
    context.write('Readout Time (s) = ' + str(RT))
    context.write('Matrix Size (voxels) = ' + str(dimx) + ' x ' + str(dimy) + ' x ' + str(dimz))
    context.write('Phase-encoding direction along ' + PE)

    #store these additional dicom informations to .minf file :
    # minf = {}
    # minf['Manufacturer'] = manufact
    # minf['TR'] = TR
    # minf['TE'] = TE
    # minf['Bandwith_per_Pixel_PhaseEncode_Hz'] = BdWpp
    # minf['Effective_Echo_Spacing'] = ESeff
    # minf['ReadOut_Time_s'] = RT
    # minf['Matrix_Voxel_Size'] = tuple(dimx,dimy,dimz)
    # minf['Phase Encoding Direction'] = PE
    #
    # self.output_dwi_data.updateMinf(minf, saveMinf=True)


