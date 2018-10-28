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
from soma.aims import fslTransformation
from brainvisa.registration import getTransformationManager
import numpy

name = 'Diffusion to T1 non linear reg (FNIRT)'
userLevel = 0

signature=Signature(

    'b0_volume', ReadDiskItem( 'B0 Volume', 'gz compressed NIFTI-1 image' ),
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
    'T1_to_b0_interpolation', Choice('spline',
                           'trilinear',
                           'nn',
                           'sinc'),
    # 'T1_to_b0_resampling', Boolean(),
    'T1_to_b0', WriteDiskItem('T1 MRI to DW Diffusion MR' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_mask', WriteDiskItem('T1 MRI to DW Diffusion MR Brain' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_GM', WriteDiskItem('T1 MRI to DW Diffusion MR GM' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_WM', WriteDiskItem('T1 MRI to DW Diffusion MR WM' , 'gz compressed NIFTI-1 image' ),
    'T1_to_b0_skeleton', WriteDiskItem('T1 MRI to DW Diffusion MR Skeleton', 'gz compressed NIFTI-1 image' ),
    'diff_to_T1_linear_xfm', WriteDiskItem( 'Transform Diffusion MR to T1 MRI', 'Transformation matrix' ),
    'diff_to_T1_nonlinear_dfm', WriteDiskItem( 'NL Deform Diffusion MR to T1 MRI', 'gz compressed NIFTI-1 image' ),
    'T1_to_diff_linear_xfm', WriteDiskItem( 'Transform T1 MRI to Diffusion MR', 'Transformation matrix' ),
    'T1_to_diff_nonlinear_dfm', WriteDiskItem( 'NL Deform T1 MRI to Diffusion MR', 'gz compressed NIFTI-1 image' ),
)

def initialization( self ):
    self.linkParameters( 'T1_mask', 'T1_volume' )
    self.linkParameters( 'T1_grey_white_left', 'T1_volume' )
    self.linkParameters( 'T1_grey_white_right', 'T1_volume' )
    self.linkParameters( 'T1_skeleton_left', 'T1_volume' )
    self.linkParameters( 'T1_skeleton_right', 'T1_volume' )
    self.linkParameters('dwi_data', 'b0_volume')
    self.linkParameters('bvals', 'dwi_data')
    self.linkParameters('bvecs', 'dwi_data')
    self.linkParameters( 'b0_to_T1', 'b0_volume' )
    self.linkParameters( 'T1_to_b0', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_mask', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_GM', 'b0_volume' )
    self.linkParameters( 'T1_to_b0_WM', 'b0_volume' )
    self.linkParameters('T1_to_b0_skeleton', 'b0_volume')
    # self.T1_to_b0_resampling = False
    self.linkParameters( 'diff_to_T1_linear_xfm', 'b0_volume' )
    self.linkParameters( 'diff_to_T1_nonlinear_dfm', 'b0_volume' )
    self.linkParameters( 'T1_to_diff_linear_xfm', 'b0_volume' )
    self.linkParameters( 'T1_to_diff_nonlinear_dfm', 'b0_volume' )

def execution( self, context ):

    configuration = Application().configuration
    transformManager = getTransformationManager()

    context.write('Fractional anisotropy temporary estimation')
    dtifit = context.temporary('File')
    mask = context.temporary('File')
    cmd = [configuration.FSL.fsl_commands_prefix + 'bet', self.b0_volume.fullPath(), mask.fullPath(), '-f', '0.3', '-m']
    context.system(*cmd)
    cmd = [configuration.FSL.fsl_commands_prefix + 'dtifit', '-k', self.dwi_data.fullPath(), '-o', dtifit.fullPath(), '-m', mask.fullPath() + '_mask.nii.gz', '-r', self.bvecs.fullPath(), '-b', self.bvals.fullPath() ]
    context.system(*cmd)
    FA = dtifit.fullPath() + '_FA.nii.gz'

    context.write('Fractional anisotropy bias correction')
    bias_corr = context.temporary('File')
    cmd = [configuration.FSL.fsl_commands_prefix + 'fsl_anat', '-i', FA, '-o', bias_corr.fullPath(), '-t', 'T2', '--clobber', '--strongbias', '--noreorient', '--nocrop', '--noreg', '--nononlinreg', '--noseg', '--nosubcortseg']
    context.system(*cmd)
    FA_biascorr = bias_corr.fullPath() + '.anat/T2_biascorr.nii.gz'

    context.write('T1 white-matter segmentation')
    t1_brain = context.temporary( 'NIFTI-1 image' )
    fast_seg = context.temporary('File')
    T1_mask_bin = context.temporary('NIFTI-1 image')
    cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.T1_mask.fullPath(), '-bin', T1_mask_bin]
    context.system(*cmd)
    context.system('AimsMask', '-i', self.T1_volume, '-m', T1_mask_bin.fullPath(), '-o', t1_brain.fullPath())
    cmd = [configuration.FSL.fsl_commands_prefix + 'fast', '-o', fast_seg.fullPath(), t1_brain.fullPath()]
    context.system(*cmd)
    T1_white_matter = fast_seg.fullPath() + '_pve_2.nii.gz'

    context.write('Affine pre-alignment')
    diff_to_t1_lin = context.temporary('File')
    cmd = [configuration.FSL.fsl_commands_prefix + 'flirt', '-ref', T1_white_matter, '-in', FA_biascorr, '-dof', '6', '-omat', diff_to_t1_lin.fullPath()]
    context.system(*cmd)

    context.write('Non linear registration')
    cmd = [configuration.FSL.fsl_commands_prefix + 'fnirt', '--ref=' + T1_white_matter, '--in=' + FA_biascorr, '--aff=' + diff_to_t1_lin.fullPath(), '--cout=' + self.diff_to_T1_nonlinear_dfm.fullPath(), '--refmask=' + T1_mask_bin.fullPath(), '--intmod=global_linear']
    context.system(*cmd)
    cmd = [configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', self.b0_volume.fullPath(), '-r', T1_white_matter, '-o', self.b0_to_T1.fullPath(), '-w', self.diff_to_T1_nonlinear_dfm.fullPath(), '--interp=spline']
    context.system(*cmd)
    transformManager.copyReferential(self.T1_volume, self.b0_to_T1)

    ## Non applicable to non-linear warp image
    ## To compute only for anatomist to load files in the same referential
    context.write('Conversion from .mat to .trm')
    trm = fslTransformation.fslMatToTrm(diff_to_t1_lin.fullPath(), self.b0_volume.fullPath(), self.b0_to_T1.fullPath())
    aims.write(trm, self.diff_to_T1_linear_xfm.fullPath())
    context.write('Invert transformation...')
    cmd = [ 'AimsInvertTransformation', '-i', self.diff_to_T1_linear_xfm, '-o', self.T1_to_diff_linear_xfm ]
    context.system( *cmd )
    cmd = [configuration.FSL.fsl_commands_prefix + 'invwarp', '--ref=' + self.b0_volume.fullPath(), '--warp=' + self.diff_to_T1_nonlinear_dfm.fullPath(), '--out=' + self.T1_to_diff_nonlinear_dfm.fullPath()]
    context.system(*cmd)

    context.write('Registration of T1 to DWI space...')
    print(self.T1_to_b0_interpolation)
    cmd = [configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', self.T1_volume.fullPath(), '-r', self.b0_volume.fullPath(), '-o', self.T1_to_b0.fullPath(), '-w', self.T1_to_diff_nonlinear_dfm.fullPath(), '--interp=' + self.T1_to_b0_interpolation]
    context.system(*cmd)
    transformManager.copyReferential( self.b0_volume, self.T1_to_b0 )

    context.write('Registration of T1 brain mask to DWI space...')
    cmd = [configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', self.T1_mask.fullPath(), '-r', self.b0_volume.fullPath(), '-o', self.T1_to_b0_mask.fullPath(), '-w', self.T1_to_diff_nonlinear_dfm.fullPath(), '--interp=' + self.T1_to_b0_interpolation]
    context.system(*cmd)
    cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.T1_to_b0_mask.fullPath(), '-bin', self.T1_to_b0_mask.fullPath()]
    context.system(*cmd)
    transformManager.copyReferential(self.b0_volume, self.T1_to_b0_mask)

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
    cmd = [configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', GM_file.fullPath(), '-r', self.b0_volume.fullPath(), '-o', self.T1_to_b0_GM.fullPath(), '-w', self.T1_to_diff_nonlinear_dfm.fullPath(), '--interp=nn']
    context.system(*cmd)
    cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.T1_to_b0_GM.fullPath(), '-thr', '50', '-bin', self.T1_to_b0_GM.fullPath()]
    context.system(*cmd)
    transformManager.copyReferential( self.b0_volume, self.T1_to_b0_GM )
    cmd = [configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', WM_file.fullPath(), '-r', self.b0_volume.fullPath(), '-o', self.T1_to_b0_WM.fullPath(), '-w', self.T1_to_diff_nonlinear_dfm.fullPath(), '--interp=nn']
    context.system(*cmd)
    cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.T1_to_b0_WM.fullPath(), '-thr', '50', '-bin', self.T1_to_b0_WM.fullPath()]
    context.system(*cmd)
    transformManager.copyReferential(self.b0_volume, self.T1_to_b0_WM)

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
    cmd = [configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', skeleton_file.fullPath(), '-r', self.b0_volume.fullPath(), '-o', self.T1_to_b0_skeleton.fullPath(), '-w', self.T1_to_diff_nonlinear_dfm.fullPath(), '--interp=nn']
    context.system(*cmd)
    cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.T1_to_b0_skeleton.fullPath(), '-bin', self.T1_to_b0_skeleton.fullPath()]
    context.system(*cmd)
    transformManager.copyReferential(self.b0_volume, self.T1_to_b0_skeleton)
    cmd = ['AimsMask', '-i', self.T1_to_b0_skeleton, '-o', self.T1_to_b0_skeleton, '-m', self.T1_to_b0_WM, '--inv', 'True']
    context.system(*cmd)

    context.write('Finished')

