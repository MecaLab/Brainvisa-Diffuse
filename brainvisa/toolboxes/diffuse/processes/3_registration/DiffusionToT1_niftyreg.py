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
    #checking for Niftyreg commands
    cmds = ['reg_f3d','reg_resample','reg_transform']
    for i, cmd in enumerate(cmds):
        executable = find_executable(cmd)
        if not executable:
           raise ValidationError(cmd + 'command was not found.Please check your Niftyreg installation and/or version')
    #checking for FSl's commands
    cmds = ['bet','flirt','dtifit']
    for i, cmd in enumerate(cmds):
        executable = find_executable(fsl_prefix + cmd)
        if not executable:
           raise ValidationError(cmd + 'FSL command was not found.Please check your FSL installation and/or fsldir and fsl_commands_prefix setting in BranVISA')
    pass
   

from brainvisa.processes import *
from soma.wip.application.api import Application
from soma.aims import fslTransformation
from brainvisa.registration import getTransformationManager
from distutils.spawn import find_executable
import numpy
import os

name = 'Diffusion to T1 non linear reg (NIFTYREG)'
userLevel = 0

signature=Signature(

    'b0_volume', ReadDiskItem( 'B0 Volume', 'Aims readable volume formats' ),
    'dwi_data', ReadDiskItem( 'Corrected DW Diffusion MR', 'Aims readable volume formats'),
    'bvals', ReadDiskItem( 'Raw B Values', 'Text file' ),
    'bvecs', ReadDiskItem( 'Corrected B Vectors', 'Text file' ),
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
    'diff_to_T1_nonlinear_dfm', WriteDiskItem( 'NL Deform Diffusion MR to T1 MRI', 'NIFTI-1 image' ),
    'T1_to_diff_linear_xfm', WriteDiskItem( 'Transform T1 MRI to Diffusion MR', 'Transformation matrix' ),
    'T1_to_diff_nonlinear_dfm', WriteDiskItem( 'NL Deform T1 MRI to Diffusion MR', 'NIFTI-1 image' ),
)

def initialization( self ):
    self.linkParameters( 'T1_mask', 'T1_volume' )
    self.linkParameters( 'T1_grey_white_left', 'T1_volume' )
    self.linkParameters( 'T1_grey_white_right', 'T1_volume' )
    self.linkParameters( 'T1_skeleton_left', 'T1_volume' )
    self.linkParameters( 'T1_skeleton_right', 'T1_volume' )
    self.linkParameters( 'dwi_data', 'b0_volume')
    self.linkParameters( 'bvals', 'dwi_data')
    self.linkParameters( 'bvecs', 'dwi_data')
    self.linkParameters( 'b0_to_T1', 'b0_volume' )
    self.linkParameters( 'T1_to_b0', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_mask', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_GM', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_WM', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_skeleton', 'b0_volume')
    self.linkParameters( 'diff_to_T1_linear_xfm', 'b0_volume' )
    self.linkParameters( 'diff_to_T1_nonlinear_dfm', 'b0_volume' )
    self.linkParameters( 'T1_to_diff_linear_xfm', 'b0_volume' )
    self.linkParameters( 'T1_to_diff_nonlinear_dfm', 'b0_volume' )
    self.T1_to_b0_resampling = False

def execution( self, context ):

    configuration = Application().configuration
    transformManager = getTransformationManager()
    niftyreg_f3d = find_executable('reg_f3d')
    niftyreg_resample = find_executable('reg_resample')
    niftyreg_transform = find_executable('reg_transform')
    

    context.write('Fractional anisotropy temporary estimation')
    dtifit = context.temporary('File')
    mask = context.temporary('File')
    cmd = [configuration.FSL.fsl_commands_prefix + 'bet', self.b0_volume.fullPath(), mask.fullPath(), '-f', '0.3', '-m']
    context.system(*cmd)
    cmd = [configuration.FSL.fsl_commands_prefix + 'dtifit', '-k', self.dwi_data.fullPath(), '-o', dtifit.fullPath(), '-m', mask.fullPath() + '_mask.nii.gz', '-r', self.bvecs.fullPath(), '-b', self.bvals.fullPath() ]
    context.system(*cmd)
    FA = dtifit.fullPath() + '_FA.nii.gz'

    context.write('Affine pre-alignment')
    diff_to_t1_xfm = context.temporary('File') #'/tmp/diff_to_t1_xfm' #
    reg = context.temporary('File') #'/tmp/reg' #
    t1_brain = context.temporary('NIFTI-1 image')
    context.system('AimsMask', '-i', self.T1_volume, '-m', self.T1_mask.fullPath(), '-o', t1_brain.fullPath())
    cmd = [configuration.FSL.fsl_commands_prefix + 'flirt', '-ref', t1_brain.fullPath(), '-in', FA, '-omat', diff_to_t1_xfm.fullPath() + '_init.mat', '-out', reg.fullPath()+'_FA_to_t1_affine.nii.gz']
    context.system(*cmd)
    #diff_to_t1_xfm.fullPath() is an affine 4X4 matrix
    cmd = [configuration.FSL.fsl_commands_prefix + 'flirt', '-ref', t1_brain.fullPath(), '-in', self.b0_volume.fullPath(), '-applyxfm', '-init', diff_to_t1_xfm.fullPath() + '_init.mat', '-out', reg.fullPath() + '_b0_to_t1_affine.nii.gz']
    context.system(*cmd)
    #register the bo into the T1 space using affine transformation

    tmp_file = context.temporary('gz compressed NIFTI-1 image')

    context.write('Non linear registration')
    cmd = [niftyreg_f3d, '-ref', self.T1_volume.fullPath(), '-flo', reg.fullPath()+'_FA_to_t1_affine.nii.gz', '-sym', '-cpp', diff_to_t1_xfm.fullPath() + '_cpp.nii', '-res', reg.fullPath()+'_FA_to_t1_nonlinear.nii.gz']
    context.system(*cmd)
    cmd = [niftyreg_resample, '-ref', self.T1_volume.fullPath(), '-flo', reg.fullPath()+'_b0_to_t1_affine.nii.gz', '-trans', diff_to_t1_xfm.fullPath() + '_cpp.nii', '-res', tmp_file.fullPath()]
    context.system(*cmd)
    ref = self.T1_volume.get( 'storage_to_memory', search_header=True )
    context.system('AimsFileConvert', '-i', tmp_file.fullPath(), '-o', self.b0_to_T1.fullPath(), '--orient', '"abs: '+' '.join(map(str, ref))+'"')
    transformManager.copyReferential(self.T1_volume, self.b0_to_T1)

    context.write('Invert transformation...')
    cmd = [niftyreg_transform, '-ref', self.T1_volume.fullPath(), '-def', diff_to_t1_xfm.fullPath() + '_cpp.nii', self.diff_to_T1_nonlinear_dfm.fullPath()]
    context.system(*cmd)
    cmd = [niftyreg_transform, '-ref', self.T1_volume.fullPath(), '-def', diff_to_t1_xfm.fullPath() + '_cpp_backward.nii', self.T1_to_diff_nonlinear_dfm.fullPath()] #reg.fullPath()+'_FA_to_t1_affine.nii.gz'
    context.system(*cmd)
    # cmd = [configuration.FSL.fsl_commands_prefix + 'convert_xfm', '-omat', diff_to_t1_xfm.fullPath() + '_init_inv.mat', '-inverse', diff_to_t1_xfm.fullPath() + '_init.mat']
    # context.system(*cmd)
    context.write('Conversion from .mat to .trm')  # Non applicable to non-linear warp image. To compute only for anatomist to load files in the same referential
    trm = fslTransformation.fslMatToTrm(diff_to_t1_xfm.fullPath() + '_init.mat', self.b0_volume.fullPath(), self.b0_to_T1.fullPath())
    aims.write(trm, self.diff_to_T1_linear_xfm.fullPath())
    cmd = ['AimsInvertTransformation', '-i', self.diff_to_T1_linear_xfm, '-o', self.T1_to_diff_linear_xfm]
    context.system(*cmd)

    context.write('Registration of T1 to DWI space...')
    cmd = [niftyreg_resample, '-ref', self.T1_volume.fullPath(), '-flo', self.T1_volume.fullPath(), '-trans', self.T1_to_diff_nonlinear_dfm.fullPath(), '-res', tmp_file.fullPath()] #reg.fullPath()+'_FA_to_t1_affine.nii.gz'
    context.system(*cmd)
    cmd = ['AimsResample', '-i', tmp_file, '-m', self.T1_to_diff_linear_xfm, '-t', self.T1_to_b0_interpolation, '-o', self.T1_to_b0]
    if self.T1_to_b0_resampling == True:
        cmd += ['-r', self.b0_volume]
    elif self.T1_to_b0_resampling == False:
        dim = self.b0_volume.get('volume_dimension', search_header=True)
        vox_ref = self.b0_volume.get('voxel_size', search_header=True)
        vox_in = self.T1_volume.get('voxel_size', search_header=True)
        cmd += ['--dx', str(int(dim[0] * vox_ref[0] / vox_in[0]) + 1), '--dy', str(int(dim[1] * vox_ref[1] / vox_in[1]) + 1), '--dz', str(int(dim[2] * vox_ref[2] / vox_in[2]) + 1)]
    context.system(*cmd)
    ref = self.b0_volume.get('storage_to_memory', search_header=True)
    os.system(' '.join(['AimsFileConvert', '-i', self.T1_to_b0.fullPath(), '-o', self.T1_to_b0.fullPath(), '--orient', '"abs: ' + ' '.join(map(str, ref)) + '"']))
    transformManager.copyReferential( self.b0_volume, self.T1_to_b0 )

    context.write('Registration of T1 brain mask to DWI space...')
    cmd = [niftyreg_resample, '-ref', self.T1_volume.fullPath(), '-flo', self.T1_mask.fullPath(), '-trans', self.T1_to_diff_nonlinear_dfm.fullPath(), '-res', tmp_file.fullPath()] #reg.fullPath()+'_FA_to_t1_affine.nii.gz'
    context.system(*cmd)
    cmd = ['AimsResample', '-i', tmp_file, '-m', self.T1_to_diff_linear_xfm, '-t', self.T1_to_b0_interpolation, '-o', self.T1_to_b0_mask, '-r', self.b0_volume]
    context.system(*cmd)
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_mask, '-o', self.T1_to_b0_mask, '-t', '1', '-b', '--fg', '1']
    context.system(*cmd)
    os.system(' '.join(['AimsFileConvert', '-i', self.T1_to_b0_mask.fullPath(), '-o', self.T1_to_b0_mask.fullPath(), '--orient', '"abs: ' + ' '.join(map(str, ref)) + '"']))
    transformManager.copyReferential(self.dwi_data, self.T1_to_b0_mask)

    context.write('Recompile left-right grey-matter and white-matter...')
    Left = aims.read(self.T1_grey_white_left.fullPath())
    Right = aims.read(self.T1_grey_white_right.fullPath())
    Left_Right = Left + Right
    GM = Left.arraydata()
    GM[:, :, :, :] = 0
    GM[numpy.where(Left_Right.arraydata() == 100)] = 100
    WM = Right.arraydata()
    WM[:, :, :, :] = 0
    WM[numpy.where(Left_Right.arraydata() == 200)] = 100
    GM_vol = aims.Volume(GM)
    WM_vol = aims.Volume(WM)
    GM_vol.copyHeaderFrom(Left.header())
    WM_vol.copyHeaderFrom(Left.header())
    GM_file = context.temporary('NIFTI-1 image')
    WM_file = context.temporary('NIFTI-1 image')
    aims.write(GM_vol, GM_file.fullPath())
    aims.write(WM_vol, WM_file.fullPath())

    context.write('Registration of white-matter and grey-matter masks to DWI space...')
    cmd = [niftyreg_resample, '-ref', self.T1_volume.fullPath(), '-flo', GM_file.fullPath(), '-trans', self.T1_to_diff_nonlinear_dfm.fullPath(), '-res', tmp_file.fullPath(), '-inter', 0 ] #reg.fullPath()+'_FA_to_t1_affine.nii.gz'
    context.system(*cmd)
    cmd = ['AimsResample', '-i', tmp_file, '-m', self.T1_to_diff_linear_xfm, '-t', '0', '-o', self.T1_to_b0_GM, '-d', '1', '-r', self.b0_volume]
    context.system(*cmd)
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_GM, '-o', self.T1_to_b0_GM, '-t', '50', '-b', '--fg', '1']
    context.system(*cmd)
    os.system(' '.join(['AimsFileConvert', '-i', self.T1_to_b0_GM.fullPath(), '-o', self.T1_to_b0_GM.fullPath(), '--orient', '"abs: ' + ' '.join(map(str, ref)) + '"']))
    transformManager.copyReferential(self.dwi_data, self.T1_to_b0_GM)
    cmd = [niftyreg_resample, '-ref', self.T1_volume.fullPath(), '-flo', WM_file.fullPath(), '-trans', self.T1_to_diff_nonlinear_dfm.fullPath(), '-res', tmp_file.fullPath(), '-inter', '0'] #reg.fullPath()+'_FA_to_t1_affine.nii.gz'
    context.system(*cmd)
    cmd = ['AimsResample', '-i', tmp_file, '-m', self.T1_to_diff_linear_xfm, '-t', '0', '-o', self.T1_to_b0_WM, '-d', '1', '-r', self.b0_volume]
    # cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.T1_to_b0_WM.fullPath(), '-thr', '50', '-bin', self.T1_to_b0_WM.fullPath()]
    context.system(*cmd)
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_WM, '-o', self.T1_to_b0_WM, '-t', '50', '-b', '--fg', '1']
    context.system(*cmd)
    os.system(' '.join(['AimsFileConvert', '-i', self.T1_to_b0_WM.fullPath(), '-o', self.T1_to_b0_WM.fullPath(), '--orient', '"abs: ' + ' '.join(map(str, ref)) + '"']))
    transformManager.copyReferential(self.dwi_data, self.T1_to_b0_WM)

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
    cmd = [niftyreg_resample, '-ref', self.T1_volume.fullPath(), '-flo', skeleton_file.fullPath(), '-trans', self.T1_to_diff_nonlinear_dfm.fullPath(), '-res', tmp_file.fullPath()] #reg.fullPath()+'_FA_to_t1_affine.nii.gz'
    context.system(*cmd)
    cmd = ['AimsResample', '-i', tmp_file, '-m', self.T1_to_diff_linear_xfm, '-t', '0', '-o', self.T1_to_b0_skeleton, '-r', self.b0_volume]
    context.system(*cmd)
    cmd = ['AimsThreshold', '-i', self.T1_to_b0_skeleton, '-o', self.T1_to_b0_skeleton, '-m', 'gt', '-t', '0', '-b', '--fg', '1']
    context.system(*cmd)
    cmd = ['AimsMask', '-i', self.T1_to_b0_skeleton, '-o', self.T1_to_b0_skeleton, '-m', self.T1_to_b0_WM, '--inv', 'True']
    context.system(*cmd)
    os.system(' '.join(['AimsFileConvert', '-i', self.T1_to_b0_skeleton.fullPath(), '-o', self.T1_to_b0_skeleton.fullPath(), '--orient', '"abs: ' + ' '.join(map(str, ref)) + '"']))
    transformManager.copyReferential(self.dwi_data, self.T1_to_b0_skeleton)
    context.write('Finished')

