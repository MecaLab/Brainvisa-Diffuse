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
from soma.wip.application.api import Application
from distutils.spawn import find_executable
import brainvisa.tools.aimsGlobals as aimsGlobals
import os

name = 'Apply T1 to Diffusion transform to ROI'
userLevel = 0

signature=Signature(
    'b0_volume', ReadDiskItem( 'B0 Volume', 'gz compressed NIFTI-1 image' ),
    'T1_volume', ReadDiskItem( 'T1 MRI Bias Corrected', 'Aims readable volume formats' ),
    'ROI_in_T1', ReadDiskItem( '3D Volume', aimsGlobals.aimsVolumeFormats ),
    'lower_thresh', Number(),
    'upper_thresh', Number(),
    'binarise', Boolean(),
    'threshold', Number(),
    'T1_to_b0_registration_method', Choice("niftyreg", "fnirt"),
    'T1_to_diff_linear_xfm', WriteDiskItem( 'Transform T1 MRI to Diffusion MR', 'Transformation matrix' ),
    'T1_to_diff_nonlinear_dfm', WriteDiskItem( 'NL Deform T1 MRI to Diffusion MR', 'NIFTI-1 image' ),

    'ROI_in_DWI', WriteDiskItem('3D Volume' , aimsGlobals.aimsVolumeFormats ),
)

def initialization( self ):
    self.resampling = False
    self.binarise = True
    self.threshold = 0.5
    self.setOptional('lower_thresh')
    self.setOptional('upper_thresh')
    self.linkParameters( 'T1_to_diff_linear_xfm', 'b0_volume' )
    self.linkParameters( 'T1_to_diff_nonlinear_dfm', 'b0_volume' )
    self.T1_to_b0_registration_method = 'niftyreg'

def execution( self, context ):

    configuration = Application().configuration
    transformManager = getTransformationManager()
    niftyreg_resample = find_executable('reg_resample')
    if not niftyreg_resample:
        raise RuntimeError(_t_('Niftyreg executable NOT found !'))

    reg = context.temporary('File')
    tmp_file = context.temporary('gz compressed NIFTI-1 image')

    cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.ROI_in_T1.fullPath()]
    if self.lower_thresh is not None:
        cmd += ['-thr', self.lower_thresh]
    if self.upper_thresh is not None:
        cmd += ['-uthr', self.upper_thresh]
    cmd += ['-bin', tmp_file.fullPath()]
    context.system(*cmd)

    ## A SUPPRIMER EN DEHORS DU HCP : A CAUSE ORIENTATION RAS A POSTERIORI
    # tmp_b0 = context.temporary('gz compressed NIFTI-1 image')
    # os.system(' '.join(['AimsFileConvert', '-i', self.b0_volume.fullPath(), '-o', tmp_b0.fullPath(), '--orient', '"abs: 1 -1 -1"']))
    ##

    if self.T1_to_b0_registration_method == 'niftyreg':
        cmd = [niftyreg_resample, '-ref', self.T1_volume.fullPath(), '-flo', tmp_file.fullPath(), '-def', self.T1_to_diff_nonlinear_dfm.fullPath(), '-res', reg.fullPath()+'_ROI.nii.gz', '-NN', '1']
        context.system(*cmd)
        cmd = ['AimsResample', '-i', reg.fullPath()+'_ROI.nii.gz', '-m', self.T1_to_diff_linear_xfm, '-t', '0', '-o', self.ROI_in_DWI, '-d', '1', '-r', self.b0_volume.fullPath()]
        context.system(*cmd)

    elif self.T1_to_b0_registration_method == 'fnirt':
        cmd = [configuration.FSL.fsl_commands_prefix + 'applywarp', '-i', tmp_file.fullPath(), '-r', self.b0_volume.fullPath(), '-o', self.ROI_in_DWI.fullPath(), '-w', self.T1_to_diff_nonlinear_dfm.fullPath(), '--interp=nn']
        context.system(*cmd)

    if self.binarise == True:
        cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.ROI_in_DWI.fullPath(), '-thr', self.threshold, '-bin', self.ROI_in_DWI.fullPath()]  # , '--fg', '1']
    else:
        cmd = [configuration.FSL.fsl_commands_prefix + 'fslmaths', self.ROI_in_DWI.fullPath(), '-thr', self.threshold, self.ROI_in_DWI.fullPath()]  # , '--fg', '1']
    context.system(*cmd)
    # ref = self.b0_volume.get('storage_to_memory', search_header=True)
    # transformManager.copyReferential(self.b0_volume, self.ROI_in_DWI)

    ## A SUPPRIMER EN DEHORS DU HCP : A CAUSE ORIENTATION RAS A POSTERIORI
    # os.system(' '.join(['AimsFileConvert', '-i', self.ROI_in_DWI.fullPath(), '-o', self.ROI_in_DWI.fullPath(), '--orient', '"abs: -1 -1 -1"']))
    ##

    context.write('Finished')
