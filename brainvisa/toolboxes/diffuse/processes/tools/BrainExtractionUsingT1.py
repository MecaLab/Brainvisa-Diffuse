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
from brainvisa.registration import getTransformationManager

name = 'Brain extraction using T1 mask'
userLevel = 0

signature=Signature(
    'b0_volume', ReadDiskItem( 'B0 Volume', 'Aims readable volume formats' ),
    'T1_to_b0_mask', ReadDiskItem('T1 MRI to DW Diffusion MR Brain' , 'gz compressed NIFTI-1 image' ),
    'b0_brain', WriteDiskItem( 'B0 Volume Brain', 'gz compressed NIFTI-1 image' ),
    'b0_brain_mask', WriteDiskItem( 'B0 Volume Brain Mask', 'gz compressed NIFTI-1 image' ),
)

def initialization( self ):
  self.linkParameters( 'T1_to_b0_mask', 'b0_volume' )
  self.linkParameters( 'b0_brain', 'b0_volume' )
  self.linkParameters( 'b0_brain_mask', 'b0_volume' )
  
def execution( self, context ):

    context.write('Brain extraction using T1 mask')
    
    mask_bin = context.temporary('gz compressed NIFTI-1 image')
    cmd = [ 'AimsThreshold', '-i', self.T1_to_b0_mask, '-o', mask_bin, '-m', 'gt', '-t', '0', '-b', '--fg', '1' ]
    context.system( *cmd )
    cmd = [ 'AimsMorphoMath', '-i', mask_bin, '-o', self.b0_brain_mask, '-r', '10', '-m', 'clo' ]
    context.system( *cmd )
    cmd = [ 'AimsMask', '-i', self.b0_volume, '-o', self.b0_brain, '-m', self.b0_brain_mask ]
    context.system( *cmd )
    transformManager = getTransformationManager()
    transformManager.copyReferential( self.b0_volume, self.b0_brain )
    transformManager.copyReferential( self.b0_volume, self.b0_brain_mask )

    context.write('Finished')
    
