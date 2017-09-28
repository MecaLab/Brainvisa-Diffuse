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
from registration import getTransformationManager
import numpy
from copy import copy

name = 'Import diffusion data (nifti)'
userLevel = 0
roles = ( 'importer' )

signature=Signature(
  'dwi_data', ReadDiskItem( 'Diffusion MR', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),
  'bvals', ReadDiskItem( 'B Values', 'BValues' ),
  'bvecs', ReadDiskItem( 'B Vectors', 'BVectors' ),
  'additional_acquisition', Choice("None", "Fieldmap", "Blip-reversed images", "Both"),
  'blip_reversed_data', ReadDiskItem( 'Diffusion MR', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),
  'fieldmap', ReadDiskItem( 'Fieldmap', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),
  'magnitude', ReadDiskItem( 'Fieldmap', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),

  'output_dwi_data', WriteDiskItem( 'Raw Diffusion MR', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),
  'output_bvals', WriteDiskItem( 'Raw B Values', 'Text file' ),
  'output_bvecs', WriteDiskItem( 'Raw B Vectors', 'Text file' ),
  'output_blip_reversed_data', WriteDiskItem( 'Blip Reversed DW Diffusion MR', ['gz compressed NIFTI-1 image', 'NIFTI-1 image'] ),
  'output_fieldmap', WriteDiskItem( 'Fieldmap Phase', 'gz compressed NIFTI-1 image' ),
  'output_magnitude', WriteDiskItem( 'Fieldmap Magnitude', 'gz compressed NIFTI-1 image' ),
)
def switchSignature( self, additional_acquisition ):
    signature = copy( self.signature )
    self.setOptional('blip_reversed_data')
    self.setOptional('fieldmap')
    self.setOptional('magnitude')
    self.setOptional('output_blip_reversed_data')
    self.setOptional('output_fieldmap')
    self.setOptional('output_magnitude')
    self.setHidden('blip_reversed_data')
    self.setHidden('fieldmap')
    self.setHidden('magnitude')
    self.setHidden('output_blip_reversed_data')
    self.setHidden('output_fieldmap')
    self.setHidden('output_magnitude')
    if self.additional_acquisition=="Fieldmap":
        self.setEnable('fieldmap')
        self.setEnable('magnitude')
        self.setEnable('output_fieldmap')
        self.setEnable('output_magnitude')
    elif self.additional_acquisition=="Blip-reversed images":
        self.setEnable('blip_reversed_data')
        self.setEnable('output_blip_reversed_data')
    elif self.additional_acquisition == "Both":
        self.setEnable('fieldmap')
        self.setEnable('magnitude')
        self.setEnable('output_fieldmap')
        self.setEnable('output_magnitude')
        self.setEnable('blip_reversed_data')
        self.setEnable('output_blip_reversed_data')
    self.changeSignature( signature )

def initSubject(self, inp):
    value = self.dwi_data
    if self.dwi_data is not None and isinstance(self.dwi_data, DiskItem):
        value = self.dwi_data.hierarchyAttributes()
        if value.get("subject", None) is None:
            value["subject"] = os.path.basename(
                self.dwi_data.fullPath()).partition(".")[0]
    return value
    
def initialization( self ):
  self.addLink( None, 'additional_acquisition', self.switchSignature )
  self.addLink("output_dwi_data", "dwi_data", self.initSubject)
  self.signature['dwi_data'].databaseUserLevel = 3
  self.signature['bvals'].databaseUserLevel = 3
  self.signature['bvecs'].databaseUserLevel = 3
  self.signature['blip_reversed_data'].databaseUserLevel = 3
  self.signature['fieldmap'].databaseUserLevel = 3
  self.signature['magnitude'].databaseUserLevel = 3
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
  
def execution( self, context ):
    
  # compare number of volumes and size of bvals/bvecs
  bvals = numpy.loadtxt(self.bvals.fullPath())
  bvecs = numpy.loadtxt(self.bvecs.fullPath())
  nvol = self.dwi_data.get( 'volume_dimension', search_header=True )[3]
  if sum(1 for line in open(self.bvals.fullPath())) > 1:
    raise RuntimeError( _t_( 'The b-values file must have 1 line' ))
  elif len(bvals)!=nvol:
    raise RuntimeError( _t_( 'Error: the number of 3D dwi volumes do not correspond to the number of b-values' ))
  elif bvecs.shape!=(3, nvol):
    raise RuntimeError( _t_( 'The gradient orientations file should have 3 lines and %s columns' % nvol))
  context.system( 'cp', self.bvals, self.output_bvals )
  context.system( 'cp', self.bvecs, self.output_bvecs )
  context.system('AimsFileConvert', '-i', self.dwi_data.fullPath(), '-o', self.output_dwi_data.fullPath(), '--orient', '"abs: -1 -1 -1"')
  transformManager = getTransformationManager()
  transformManager.createNewReferentialFor( self.output_dwi_data, name='Raw DW Diffusion MR' )

  if self.additional_acquisition=="Fieldmap":
      if self.fieldmap is not None:
        # fieldmap = aims.read(self.fieldmap.fullPath())
        # fieldmap_data = fieldmap.arraydata()
        # fieldmap_data_zero = aims.Volume(fieldmap_data-numpy.median(fieldmap_data[:,:,:]))
        # fieldmap_data_zero.copyHeaderFrom(fieldmap.header())
        # aims.write(fieldmap_data_zero, self.output_fieldmap.fullPath())
        context.system('AimsFileConvert', '-i', self.fieldmap.fullPath(), '-o', self.output_fieldmap.fullPath(), '--orient', '"abs: -1 -1 -1"')
      if self.magnitude is not None:
        context.system('AimsFileConvert', '-i', self.magnitude.fullPath(), '-o', self.output_magnitude.fullPath(), '--orient', '"abs: -1 -1 -1"')
  elif self.additional_acquisition=="Blip-reversed images":
    nvol_blip = self.blip_reversed_data.get( 'volume_dimension', search_header=True )[3]
    if nvol_blip == nvol:
        context.write('Full acquisiton with opposite phase-encode direction DETECTED')
    else:
        context.write('Only b0 volumes with opposite phase-encode direction DETECTED')
    context.system('AimsFileConvert', '-i', self.blip_reversed_data.fullPath(), '-o', self.output_blip_reversed_data.fullPath(), '--orient', '"abs: -1 -1 -1"')
    transformManager.copyReferential(self.output_dwi_data, self.blip_reversed_data)
  elif self.additional_acquisition=="Both":
      if self.fieldmap is not None:
        # fieldmap = aims.read(self.fieldmap.fullPath())
        # fieldmap_data = fieldmap.arraydata()
        # fieldmap_data_zero = aims.Volume(fieldmap_data-numpy.median(fieldmap_data[:,:,:]))
        # fieldmap_data_zero.copyHeaderFrom(fieldmap.header())
        # aims.write(fieldmap_data_zero, self.output_fieldmap.fullPath())
        context.system('cp', self.fieldmap, self.output_fieldmap)
      if self.magnitude is not None:
        context.system( 'cp', self.magnitude, self.output_magnitude )
      nvol_blip = self.blip_reversed_data.get('volume_dimension', search_header=True)[3]
      if nvol_blip == nvol:
          context.write('Full acquisiton with opposite phase-encode direction DETECTED')
      else:
          context.write('Only b0 volumes with opposite phase-encode direction DETECTED')
      context.system('AimsFileConvert', '-i', self.blip_reversed_data.fullPath(), '-o', self.output_blip_reversed_data.fullPath(), '--orient', '"abs: -1 -1 -1"')
      transformManager.copyReferential(self.output_dwi_data, self.blip_reversed_data)

  
  context.write( 'Importation done' )
  

