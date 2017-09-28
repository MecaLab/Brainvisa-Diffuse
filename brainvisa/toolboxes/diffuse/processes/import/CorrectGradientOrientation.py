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
import numpy
from dipy.core.gradients import gradient_table
from dipy.reconst import dti
#import anatomist.api as ana
import nibabel

name = 'Correct gradient orientation'
userLevel = 0

signature=Signature(
  'dwi_data', ReadDiskItem( 'Raw Diffusion MR', 'Aims readable volume formats' ),
  'bvals', ReadDiskItem( 'Raw B values', 'Text file' ),
  'bvecs', ReadDiskItem( 'Raw B Vectors', 'Text file' ),
  'swap_axes', Choice( "", "x/y", "y/z", "x/z" ),
  'flip_axis', Choice( "", "x", "y", "z" ),
  'visual_check', Boolean(),
  'reoriented_bvecs', WriteDiskItem( 'Reoriented B Vectors', 'Text file' ),
)

def initialization( self ):
  self.linkParameters( 'bvals', 'dwi_data' )
  self.linkParameters( 'bvecs', 'dwi_data' )
  self.setOptional('flip_axis', 'swap_axes')
  self.visual_check = True
  self.signature['reoriented_bvecs'].browseUserLevel = 3
  self.linkParameters( 'reoriented_bvecs', 'bvecs' )

def swapBvecs(bvecs, swap):
    bvecs_axes = ['x', 'y', 'z']
    if swap == 'x/y':
        indx1 = bvecs_axes.index('x')
        indx2 = bvecs_axes.index('y')
    if swap == 'y/z':
        indx1 = bvecs_axes.index('y')
        indx2 = bvecs_axes.index('z')
    if swap == 'x/z':
        indx1 = bvecs_axes.index('x')
        indx2 = bvecs_axes.index('z')
    bvecs[[indx1, indx2]] = bvecs[[indx2, indx1]]
    return bvecs

def flipBvecs(bvecs, flip):
    bvecs_axes = ['x', 'y', 'z']
    indx = bvecs_axes.index(flip)
    bvecs[indx, :] = -bvecs[indx, :]
    return bvecs

def tensorFitting(context, dwi_path, gtab):
    img = nibabel.load(dwi_path)
    data = img.get_data()
    tenmodel = dti.TensorModel(gtab)  # instantiate tensor model
    tenfit = tenmodel.fit(data)  # fit data to tensor model
    FA = dti.fractional_anisotropy(tenfit.evals)
    FA[numpy.isnan(FA)] = 0  # correct for background values
    evecs = tenfit.evecs.astype(numpy.float32)
    rgb = dti.color_fa(FA, evecs)
    
    tensor_fa = context.temporary( 'NIFTI-1 image' )
    tensor_evecs = context.temporary( 'NIFTI-1 image' )
    fa_img = nibabel.Nifti1Image(FA.astype(numpy.float32), img.get_affine())
    nibabel.save(fa_img, tensor_fa.fullPath()+'_FA.nii.gz')
    evecs_img = nibabel.Nifti1Image(evecs, img.get_affine())
    nibabel.save(evecs_img, tensor_evecs.fullPath()+'_V1.nii.gz')

    context.write('If color coding of FA map is not right, swap axes and run again')
    context.write('If orientation of principal diffusion direction does not look right, flip the axis along which slices look good')
    configuration = Application().configuration
    fsldir = configuration.FSL.fsldir
    cmd = [ '/usr/bin/fslview', tensor_fa.fullPath()+'_FA.nii.gz', tensor_evecs.fullPath()+'_V1.nii.gz' ]
    context.system(*cmd)
    
    return FA, evecs, rgb

def execution( self, context ):
    # Create gradient table
    bvals = numpy.loadtxt(self.bvals.fullPath())
    bvecs = numpy.loadtxt(self.bvecs.fullPath())
    if self.swap_axes != "":
        bvecs = swapBvecs(bvecs, self.swap_axes)
        context.write(self.swap_axes[0], 'and', self.swap_axes[2], 'axes have been swapped !')
    if self.flip_axis != "":
        bvecs = flipBvecs(bvecs, self.flip_axis)
        context.write(self.flip_axis, 'axis has been flipped !')

    if self.visual_check == True:
        context.write('Tensor fitting...')
        data_path = context.temporary( 'gz compressed NIFTI-1 image' )
        dimx = self.dwi_data.get( 'volume_dimension', search_header=True )[0]
        dimy = self.dwi_data.get( 'volume_dimension', search_header=True )[1]
        dimz = self.dwi_data.get( 'volume_dimension', search_header=True )[2]
        configuration = Application().configuration
        cmd = [ configuration.FSL.fsl_commands_prefix + 'fslroi', self.dwi_data.fullPath(), data_path.fullPath(), str(dimx/4), str(dimx/2), str(dimy/4), str(dimy/2), str(dimz/4), str(dimz/2), '0', '-1']
        context.system( *cmd )
        gtab = gradient_table(bvals, bvecs)
        [FA, evecs, rgb] = tensorFitting(context, data_path.fullPath(), gtab)

    numpy.savetxt(self.reoriented_bvecs.fullPath(), bvecs)

    

