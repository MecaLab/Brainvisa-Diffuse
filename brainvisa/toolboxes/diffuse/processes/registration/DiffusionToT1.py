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
    from soma.wip.application.api import Application
    from distutils.spawn import find_executable
    configuration = Application().configuration
    fsl_prefix = configuration.FSL.fsl_commands_prefix
    cmds = ['fast','fslmaths','flirt','applywarp']
    for i, cmd in enumerate(cmds):
        executable = find_executable(fsl_prefix + cmd)
        if not executable:
            raise ValidationError('FSL command ' + cmd + ' could not be located on your system. Please check you FSL installation and/or fsldir , fsl_commands_prefix variables in BrainVISA preferences') 
    pass

from brainvisa.processes import *
from soma.wip.application.api import Application
from soma.aims import fslTransformation
from brainvisa.registration import getTransformationManager
import numpy

name = 'Diffusion to T1 linear reg (FLIRT)'
userLevel = 0

signature=Signature(
    'b0_volume', ReadDiskItem( 'B0 Volume', 'gz compressed NIFTI-1 image' ),
    'T1_volume', ReadDiskItem( 'T1 MRI Bias Corrected', 'Aims readable volume formats' ),
    'T1_mask', ReadDiskItem( 'T1 Brain Mask', 'Aims readable volume formats' ),
    'T1_grey_white_left', ReadDiskItem( 'Left Grey White Mask', 'Aims readable volume formats', requiredAttributes = {'side':'left'}),
    'T1_grey_white_right', ReadDiskItem( 'Right Grey White Mask', 'Aims readable volume formats', requiredAttributes = {'side':'right'}),
    'T1_skeleton_left', ReadDiskItem( 'Left Cortex Skeleton', 'Aims readable volume formats', requiredAttributes = {'side':'left'}),
    'T1_skeleton_right', ReadDiskItem( 'Right Cortex Skeleton', 'Aims readable volume formats', requiredAttributes = {'side':'right'}),

    'b0_to_T1', WriteDiskItem( 'DW Diffusion MR to T1 MRI', 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_interpolation', Choice( ('linear', 1), 
                           ('quadratic', 2), 
                           ('cubic', 3), 
                           ('quartic', 4), 
                           ('quintic', 5), 
                           ('galactic', 6), 
                           ('intergalactic', 7)),
    'T1_to_b0_resampling', Boolean(),
    'T1_to_b0', WriteDiskItem('T1 MRI to DW Diffusion MR' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_mask', WriteDiskItem('T1 MRI to DW Diffusion MR Brain' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_GM', WriteDiskItem('T1 MRI to DW Diffusion MR GM' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_WM', WriteDiskItem('T1 MRI to DW Diffusion MR WM' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_skeleton', WriteDiskItem('T1 MRI to DW Diffusion MR Skeleton', 'gz compressed NIFTI-1 image' ),
    'diff_to_T1_linear_xfm', WriteDiskItem( 'Transform Diffusion MR to T1 MRI', 'Transformation matrix' ),
    'T1_to_diff_linear_xfm', WriteDiskItem( 'Transform T1 MRI to Diffusion MR', 'Transformation matrix' ),
)

def initialization( self ):
    self.linkParameters( 'T1_mask', 'T1_volume' )
    self.linkParameters( 'T1_grey_white_left', 'T1_volume' )
    self.linkParameters( 'T1_grey_white_right', 'T1_volume' )
    self.linkParameters( 'T1_skeleton_left', 'T1_volume' )
    self.linkParameters( 'T1_skeleton_right', 'T1_volume' )
    self.linkParameters( 'b0_to_T1', 'b0_volume' )
    self.linkParameters( 'T1_to_b0', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_mask', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_GM', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_WM', 'b0_volume' )
    self.linkParameters('T1_to_b0_skeleton', 'b0_volume')
    self.T1_to_b0_resampling = False
    self.linkParameters( 'diff_to_T1_linear_xfm', 'b0_volume' )
    self.linkParameters( 'T1_to_diff_linear_xfm', 'b0_volume' )
  

def execution( self, context ):

    configuration = Application().configuration
    transformManager = getTransformationManager()

    t1_brain = context.temporary( 'NIFTI-1 image' )
    context.system('AimsMask', '-i', self.T1_volume, '-m', self.T1_mask, '-o', t1_brain)

    diff_to_t1_xfm = context.temporary('File')
    # t1_to_diff_xfm = context.temporary('File')
    fast_seg = context.temporary('File')

    context.write('Registration of DWI to T1 space using FSL-epi_reg... [~15mn]')
    # cmd = [ configuration.FSL.fsl_commands_prefix + 'epi_reg', '-v', '--epi=' + self.b0_volume.fullPath(), '--t1=' + self.T1_volume.fullPath(), '--t1brain=' + t1_brain.fullPath(), '--out=' + diff_to_t1_xfm.fullPath() ]
    # context.system( *cmd )
    # context.system( 'cp', diff_to_t1_xfm.fullPath() + '.nii.gz', self.b0_to_T1 )
    context.write('- FAST segmentation')
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fast', '-o', fast_seg.fullPath(), t1_brain.fullPath()]
    context.system(*cmd)
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fslmaths', fast_seg.fullPath() + '_pve_2.nii.gz', '-thr', '0.5', '-bin', fast_seg.fullPath() + '_wmseg.nii.gz']
    context.system(*cmd)
    context.write('- pre-alignment 3dof')
    cmd = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-ref', t1_brain.fullPath(), '-in', self.b0_volume.fullPath(), '-dof', '3', '-omat', diff_to_t1_xfm.fullPath() + '_init.mat']
    context.system(*cmd)
    context.write('- flirt 6dof')
    cmd = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-ref', self.T1_volume.fullPath(), '-in', self.b0_volume.fullPath(), '-dof', '6', '-cost', 'bbr', '-wmseg', fast_seg.fullPath() + '_wmseg.nii.gz', '-init', diff_to_t1_xfm.fullPath() + '_init.mat', '-omat', diff_to_t1_xfm.fullPath() + '.mat', '-out', diff_to_t1_xfm.fullPath(), '-schedule', configuration.FSL.fsldir + '/etc/flirtsch/bbr.sch']
    context.system(*cmd)
    context.write('- applywarp')
    cmd = [ configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', self.b0_volume.fullPath(), '-r', self.T1_volume.fullPath(), '-o', self.b0_to_T1, '--premat=' + diff_to_t1_xfm.fullPath() + '.mat', '--interp=spline' ]
    context.system(*cmd)
    transformManager.copyReferential( self.T1_volume, self.b0_to_T1 )

    context.write('Conversion from .mat to .trm')
    trm = fslTransformation.fslMatToTrm(diff_to_t1_xfm.fullPath() + '.mat', self.b0_volume.fullPath(), diff_to_t1_xfm.fullPath())
    aims.write(trm, self.diff_to_T1_linear_xfm.fullPath())

    context.write('Invert transformation...')
    cmd = [ 'AimsInvertTransformation', '-i', self.diff_to_T1_linear_xfm, '-o', self.T1_to_diff_linear_xfm ]
    context.system( *cmd )

    context.write('Registration of T1 to DWI space...')
    cmd = [ 'AimsResample', '-i', self.T1_volume, '-m', self.T1_to_diff_linear_xfm, '-t', self.T1_to_b0_interpolation , '-o', self.T1_to_b0 ]
    if self.T1_to_b0_resampling == True:
      cmd += [ '-r', self.b0_volume ]
    elif self.T1_to_b0_resampling == False:
      dim = self.b0_volume.get( 'volume_dimension', search_header=True )
      context.write(dim)
      vox_ref = self.b0_volume.get( 'voxel_size', search_header=True )
      vox_in = self.T1_volume.get( 'voxel_size', search_header=True )
      context.write(vox_ref)
      context.write(vox_in)
      cmd+=[ '--dx', str(int(dim[0]*vox_ref[0]/vox_in[0])+1), '--dy', str(int(dim[1]*vox_ref[1]/vox_in[1])+1), '--dz', str(int(dim[2]*vox_ref[2]/vox_in[2])+1) ]
    context.system( *cmd )
    transformManager.copyReferential( self.b0_volume, self.T1_to_b0 )

    context.write('Registration of T1 brain mask to DWI space...')
    cmd = [ 'AimsResample', '-i', self.T1_mask, '-m', self.T1_to_diff_linear_xfm, '-t', self.T1_to_b0_interpolation , '-o', self.T1_to_b0_mask ]
##    if self.T1_to_b0_resampling == True:
    cmd += [ '-r', self.b0_volume ]
##    elif self.T1_to_b0_resampling == False:
##      cmd+=[ '--dx', str(dim[0]*vox_ref[0]/vox_in[0]), '--dy', str(dim[1]*vox_ref[1]/vox_in[1]), '--dz', str(dim[2]*vox_ref[2]/vox_in[2]) ]
    context.system( *cmd )
    transformManager.copyReferential( self.b0_volume, self.T1_to_b0_mask )
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_mask, '-o', self.T1_to_b0_mask, '-t', '1', '-b', '--fg', '1' ]
    context.system( *cmd)

    context.write('Recompile left-right grey-matter and white-matter...')
    Left = aims.read(self.T1_grey_white_left.fullPath())
    Right = aims.read(self.T1_grey_white_right.fullPath())
    Left_Right = Left + Right
    GM = Left.arraydata()
    GM[:,:,:,:] = 0
    GM[numpy.where(Left_Right.arraydata()==100)] = 100
    WM = Right.arraydata()
    WM[:,:,:,:] = 0
    WM[numpy.where(Left_Right.arraydata()==200)] = 100
    GM_vol = aims.Volume(GM)
    WM_vol = aims.Volume(WM)
    GM_vol.copyHeaderFrom(Left.header())
    WM_vol.copyHeaderFrom(Left.header())
    GM_file = context.temporary( 'NIFTI-1 image' )
    WM_file = context.temporary( 'NIFTI-1 image' )
    aims.write(GM_vol, GM_file.fullPath())
    aims.write(WM_vol, WM_file.fullPath())

    context.write('Registration of white-matter and grey-matter masks to DWI space...')
    cmd = [ 'AimsResample', '-i', GM_file.fullPath(), '-m', self.T1_to_diff_linear_xfm, '-t', '0' , '-o', self.T1_to_b0_GM, '-d', '1']
##    if self.T1_to_b0_resampling == True:
    cmd += [ '-r', self.b0_volume ]
##    elif self.T1_to_b0_resampling == False:
##      dim = self.b0_volume.get( 'volume_dimension', search_header=True )
##      vox_ref = self.b0_volume.get( 'voxel_size', search_header=True )
##      vox_in = self.T1_volume.get( 'voxel_size', search_header=True )
##      cmd+=[ '--dx', str(dim[0]*vox_ref[0]/vox_in[0]), '--dy', str(dim[1]*vox_ref[1]/vox_in[1]), '--dz', str(dim[2]*vox_ref[2]/vox_in[2]) ]
    context.system( *cmd )
    transformManager.copyReferential( self.b0_volume, self.T1_to_b0_GM )
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_GM, '-o', self.T1_to_b0_GM, '-t', '2', '-b', '--fg', '1' ]
    context.system( *cmd)
    cmd = [ 'AimsResample', '-i', WM_file.fullPath(), '-m', self.T1_to_diff_linear_xfm, '-t', '0' , '-o', self.T1_to_b0_WM, '-d', '1']
##    if self.T1_to_b0_resampling == True:
    cmd += [ '-r', self.b0_volume ]
##    elif self.T1_to_b0_resampling == False:
##      cmd+=[ '--dx', str(dim[0]*vox_ref[0]/vox_in[0]), '--dy', str(dim[1]*vox_ref[1]/vox_in[1]), '--dz', str(dim[2]*vox_ref[2]/vox_in[2]) ]
    context.system( *cmd )
    transformManager.copyReferential( self.b0_volume, self.T1_to_b0_WM )
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_WM, '-o', self.T1_to_b0_WM, '-t', '2', '-b', '--fg', '1' ]
    context.system( *cmd)

    context.write('Recompile T1 left-right skeletons...')
    Left = aims.read(self.T1_skeleton_left.fullPath())
    Right = aims.read(self.T1_skeleton_right.fullPath())
    Lskeleton = Left.arraydata()
    Rskeleton = Right.arraydata()
    Lskeleton[Lskeleton < 20] = 0
    Lskeleton[Lskeleton > 20] = 1
    Rskeleton[Rskeleton < 20] = 0
    Rskeleton[Rskeleton > 20] = 1
    Lskeleton_vol = aims.Volume(Lskeleton)
    Rskeleton_vol = aims.Volume(Rskeleton)
    skeleton = Lskeleton_vol + Rskeleton_vol
    skeleton.copyHeaderFrom(Left.header())
    skeleton_file = context.temporary('NIFTI-1 image')
    aims.write(skeleton, skeleton_file.fullPath())

    context.write('Registration of T1 skeleton mask to DWI space...')
    cmd = ['AimsResample', '-i', skeleton_file.fullPath(), '-m', self.T1_to_diff_linear_xfm, '-t', '0', '-o', self.T1_to_b0_skeleton, '-d', '1']
    ##    if self.T1_to_b0_resampling == True:
    cmd += ['-r', self.b0_volume]
    ##    elif self.T1_to_b0_resampling == False:
    ##      cmd+=[ '--dx', str(dim[0]*vox_ref[0]/vox_in[0]), '--dy', str(dim[1]*vox_ref[1]/vox_in[1]), '--dz', str(dim[2]*vox_ref[2]/vox_in[2]) ]
    context.system(*cmd)
    transformManager.copyReferential(self.b0_volume, self.T1_to_b0_skeleton)
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_skeleton, '-o', self.T1_to_b0_skeleton, '-t', '1', '-b', '--fg', '1']
    context.system(*cmd)
    cmd = ['AimsMask', '-i', self.T1_to_b0_skeleton, '-o', self.T1_to_b0_skeleton, '-m', self.T1_to_b0_WM, '--inv', 'True']
    context.system(*cmd)

    context.write('Finished')

