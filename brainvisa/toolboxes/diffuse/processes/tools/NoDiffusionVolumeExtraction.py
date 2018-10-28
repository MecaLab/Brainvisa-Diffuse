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
from soma.wip.application.api import Application
from brainvisa.registration import getTransformationManager
import numpy
from copy import copy

name = 'b0 (T2) volume extraction'
userLevel = 0

signature=Signature(
  'data_are_distortion_corrected', Boolean(),
  'dwi_data', ReadDiskItem( 'Raw Denoised Diffusion MR', 'Aims readable volume formats' ),
  'bvals', ReadDiskItem( 'Raw B Values', 'Text file' ),
  'b0_volume', WriteDiskItem( 'B0 Volume', 'gz compressed NIFTI-1 image' ),
)

def switchCorrection( self, data_are_distortion_corrected ):
  if self.data_are_distortion_corrected:
    dwi_type = 'Corrected DW Diffusion MR'
  else:
    dwi_type = 'Raw Denoised Diffusion MR'
  if dwi_type == self.signature[ 'dwi_data' ].type.name:
    return
  signature = copy( self.signature )
  signature[ 'dwi_data' ] = ReadDiskItem( dwi_type, 'Aims readable volume formats' )
  self.changeSignature( signature )

def initialization( self ):
  self.data_are_distortion_corrected = True
  self.addLink( None, 'data_are_distortion_corrected', self.switchCorrection )
  self.linkParameters( 'bvals', 'dwi_data' )
  self.linkParameters( 'b0_volume', 'dwi_data' )

def execution( self, context ):
    configuration = Application().configuration
  
    img = aims.read(self.dwi_data.fullPath())
    dwi_data = img.arraydata()
    bvals = numpy.loadtxt(self.bvals.fullPath())
    b0_index = numpy.where(bvals < 100)[0] ## bvals==0 not possible when bvalues take values +-5 or +-10

    if self.data_are_distortion_corrected:
        ## Average of all b0 volumes (after affine registration done by eddy-current correction)
        context.write('Average of all b0 volumes')
        b0_sum = dwi_data[b0_index[0],:,:,:]
        for ind in b0_index[1:]:
          b0_sum = b0_sum + dwi_data[ind,:,:,:]
        b0_sum = b0_sum/len(b0_index)
    else:
        ## Affine alignment and average of all b0 volumes
        refvol = context.temporary( 'NIFTI-1 image' )
        invol = context.temporary( 'NIFTI-1 image' )
        outvol = context.temporary( 'NIFTI-1 image' )
        context.write('Extraction of first b0 volume')
        cmd = [ configuration.FSL.fsl_commands_prefix + 'fslroi', self.dwi_data.fullPath(), refvol.fullPath(), str(b0_index[0]), '1' ]
        context.system( *cmd )
        b0_sum = dwi_data[b0_index[0],:,:,:]
        context.write('Affine co-registration of all b0 volumes to the first one...')
        for ind in b0_index[1:]:
          cmd = [ configuration.FSL.fsl_commands_prefix + 'fslroi', self.dwi_data.fullPath(), invol.fullPath(), str(ind), '1' ]
          context.system( *cmd )
          cmd = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-interp', 'spline', '-cost', 'mutualinfo', '-in', invol.fullPath(), '-ref', refvol.fullPath(), '-out', outvol.fullPath() ]
          context.system( *cmd )
          b0_reg = aims.read(outvol.fullPath())
          b0_reg_data = b0_reg.arraydata()
          b0_sum = b0_sum + b0_reg_data
        b0_sum = b0_sum / len(b0_index)
    # b0_sum = dwi_data[b0_index[0], :, :, :]

    b0_vol = aims.Volume(b0_sum)
    b0_vol.copyHeaderFrom(img.header())
    aims.write(b0_vol, self.b0_volume.fullPath())
    
    transformManager = getTransformationManager()
    transformManager.copyReferential( self.dwi_data, self.b0_volume )

    context.write('Finished')
