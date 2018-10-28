# This script uses a modified version of the Gibbs Tracking algorithm
# proposed by Reisert et al., NeuroImage 2011 (doi:10.1016/j.neuroimage.2010.09.016)
# The original version is available in the MITK toolkit.
# MITK is available as free open source software under a BSD-style license.
# See below:
# =======================================================================
# Copyright (c) 2003-2012 German Cancer Research Center,
# Division of Medical and Biological Informatics
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the
# following conditions are met:
#
#  * Redistributions of source code must retain the above
#    copyright notice, this list of conditions and the
#    following disclaimer.
#
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
#  * Neither the name of the German Cancer Research Center,
#    nor the names of its contributors may be used to endorse
#    or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# =======================================================================

from brainvisa.processes import *
from brainvisa.registration import getTransformationManager
from soma.wip.application.api import Application
from brainvisa.diffuse import fibertool
import brainvisa.tools.aimsGlobals as aimsGlobals
import numpy
import time
import os
import shutil
import nibabel
import scipy
from dipy.io.trackvis import save_trk
from dipy.tracking import utils

name = 'Global Gibbs Tracking'
userLevel = 1

signature=Signature(
    'dwi_data', ReadDiskItem( 'Corrected DW Diffusion MR', 'Aims readable volume formats' ),
    'bvals', ReadDiskItem( 'Raw B Values', 'Text file' ),
    'bvecs', ReadDiskItem( 'Corrected B Vectors', 'Text file'),
    'binary_mask', ReadDiskItem( 'Diffusion MR Mask' , 'Aims readable volume formats' ),
    'reconstruction_density', Choice("sparse", "dense"),
    'data_source', Choice("HCP", "CerimedMRI", "Other"), #
    'tractographyPackage', ReadDiskItem('Directory', 'Directory'),
    'streamlines', WriteDiskItem( 'Global Streamlines', 'Trackvis tracts'),
    'density_map', WriteDiskItem( 'Streamlines Density Map', 'Aims readable volume formats' ),
)

def initialization( self ):
    self.linkParameters( 'bvals', 'dwi_data')
    self.linkParameters( 'bvecs', 'dwi_data')
    self.linkParameters( 'binary_mask', 'dwi_data')
    self.linkParameters( 'streamlines', 'dwi_data')
    self.linkParameters( 'density_map', 'dwi_data')
    self.tractographyPackage = '/hpc/meca/users/brun.l/scripts/FiberTools'

def execution( self, context ):

    ## Validation
    bvals = numpy.loadtxt(self.bvals.fullPath())
    a = numpy.array(bvals) / 100
    b = numpy.round(a)
    c = numpy.unique(b)
    d = c[c != 0] * 100
    Nshell = len(d)
    if Nshell > 1:
        context.write('Multi-shell acquisition with ', str(Nshell) + ' shells: b=' + str(d.astype(int)))
        raise RuntimeError(_t_('Global Tractograhy is NOT YET COMPATIBLE with multishell acquisitions ! Please modify your data accordingly.'))
    elif Nshell == 1:
        bvalue = d[0].astype(int)

    configuration = Application().configuration
    spm = configuration.SPM.spm8_path
    matlab_exe = configuration.matlab.executable
    tractoScriptPath = fibertool.define_toolpath()
    transformManager = getTransformationManager()
    tempDir = configuration.brainvisa.temporaryDirectory
    timesec = str(int(time.time()*1000))

    MITK_bvecs = tempDir + '/MITK_bvecs.txt' #context.temporary('Text file') #
    MITK_mask = tempDir + '/MITK_mask' #context.temporary('File')
    # MITK_raw_data = tempDir + '/MITK_raw_data.mat' #context.temporary('Matlab File')
    # MITK_hardi_data = tempDir + '/MITK_hardi_data.mat' #context.temporary('Matlab File')
    MITK_tract_data = tempDir + '/MITK_tract_data_'+self.reconstruction_density+'.mat' #context.temporary('Matlab File')

    context.write("Reorganize bvecs according to MITK convention")
    # orientation: Xnew=-Y Ynew=X Znew=Z
    # b0 at the begining
    # array of shape (Nvol, 3)
    vecs = numpy.loadtxt(self.bvecs.fullPath())
    vecs[[0, 1]] = vecs[[1, 0]]
    vecs[0] = -vecs[0]
    vals = numpy.loadtxt(self.bvals.fullPath())
    b0 = numpy.where(vals < 100)[0]
    nb0 = len(b0)
    step = 0
    vecs_reorganized = numpy.copy(vecs)
    for i in range(len(vals)):
        if vals[i] < 100:
            vecs_reorganized[:, step] = vecs[:, i]
            step += 1
        else:
            vecs_reorganized[:, len(b0) + i - step] = vecs[:, i]
    new_vecs = vecs_reorganized.T
    numpy.savetxt(MITK_bvecs, new_vecs, fmt='%6f')

    context.write("Split and unzip the input 4D volume into 3D volumes")
    splitpath = tempDir+'/split_volumes_' + timesec
    if os.path.exists(splitpath):
        shutil.rmtree(splitpath)
    os.makedirs(splitpath)
    cmd = [configuration.FSL.fsl_commands_prefix + 'fslsplit', self.dwi_data.fullPath(), splitpath+'/vol_', '-t']
    context.system(*cmd)
    os.system('gunzip {0}/*'.format(splitpath))
    os.system('cp ' + self.binary_mask.fullPath() + ' ' + MITK_mask + '.nii.gz')
    os.system('gunzip -f ' + MITK_mask + '.nii.gz')

    context.write('Convert data to matlab structure')
    matfilepath = tempDir + '/fibertool_main' + timesec
    matfile = file(matfilepath + '.m', 'w')
    matfile.write("addpath(genpath('%s'));\n" % (tractoScriptPath))
    matfile.write("addpath(genpath('%s/release'));\n" % (self.tractographyPackage.fullPath()))
    matfile.write("addpath('%s');\n" % spm)
    matfile.write("fibertool_importData('%s/', '%s', '%s.nii', '%s')\n" % (splitpath, self.bvals.fullPath(), MITK_mask, tempDir))
    matfile.write("exit\n")
    matfile.close()
    os.system(matlab_exe + ' -nodisplay -r "run %s.m"' % matfilepath) #
    os.system('rm ' + matfilepath + '.m')

    context.write("Compute HARDI model and matlab structure")
    # WARNING: in calcutate_dti.m, if bvecs of b0 volumes are not equal to [0, 0, 0], then the script adds null vectors to the DE scheme artificially !
    # So size of tables are no longer equivalent. Note: It probably needs only indices in the table so it's not necessary to force them null. Actually there is even no need to reorder the bvec with b0 at the begining...
    # This issue is taken into account in our process
    computeDT = '0'
    matfilepath = tempDir + '/fibertool_hardi' + timesec
    matfile = file(matfilepath + '.m', 'w')
    matfile.write("addpath(genpath('%s'));\n" % (tractoScriptPath))
    matfile.write("addpath(genpath('%s/release'));\n" % (self.tractographyPackage.fullPath()))
    matfile.write("addpath('%s');\n" % spm)  # Fibertool is not compatible with SPM12. Need to change path in Matlab to use SPM8
    matfile.write("fibertool_computeHardi('%s', '%s', '%s', '%s', '%s')\n" % (tempDir, str(bvalue), MITK_bvecs, str(nb0), computeDT))
    matfile.write("exit\n")
    matfile.close()
    os.system(matlab_exe + ' -nodisplay -r "run %s.m"' % matfilepath) #
    os.system('rm ' + matfilepath + '.m')

    context.write("Global fiber tracking")
    threshold = '0'
    matfilepath = tempDir + '/fibertool_tracking' + timesec
    matfile = file(matfilepath + '.m', 'w')
    matfile.write("addpath(genpath('%s'));\n" % (tractoScriptPath))
    matfile.write("addpath(genpath('%s/release'));\n" % (self.tractographyPackage.fullPath()))
    matfile.write("addpath('%s');\n" % spm)
    matfile.write("fibertool_globalTracking('%s', '%s', '%s')\n" % (tempDir, threshold, self.reconstruction_density))
    matfile.write("exit\n")
    matfile.close()
    os.system(matlab_exe + ' -nodisplay -r "run %s.m"' % matfilepath) #
    os.system('rm ' + matfilepath + '.m')

    context.write('Convert .mat into .trk format')
    mask_img = nibabel.load(self.binary_mask.fullPath())
    mask = mask_img.get_data()
    print(mask.shape)
    mask_affine = mask_img.get_affine()
    if self.data_source == "HCP":
        affine = numpy.array([[1,0,0,34],[0,-1,0,144-29],[0,0,1,-23],[0,0,0,1]])
    elif self.data_source == "CerimedMRI":
        affine = numpy.array([[1,0,0,47],[0,1,0,-48],[0,0,1,-30],[0,0,0,1]]) ## To be set
    else:
        affine = numpy.eye(4)
    voxel_size = mask_img.header['pixdim'][1:4]
    scaling = numpy.array([[0,voxel_size[0],0,0],[-voxel_size[1],0,0,voxel_size[1]*(mask.shape[1])],[0,0,voxel_size[2],0],[0,0,0,1]])
    inStruct = scipy.io.loadmat(MITK_tract_data)
    context.write('tracks loaded')
    context.write(str(inStruct['curveSegCell'].shape[0]) + ' fibers detected')
    sl = []
    for s in inStruct['curveSegCell']:
        s = s[0]
        s = nibabel.affines.apply_affine(affine, s)
        s = nibabel.affines.apply_affine(scaling, s)
        sl.append(s)
    save_trk(self.streamlines.fullPath(), sl, numpy.eye(4), mask.shape)
    context.write('tractogram saved !')

    context.write('Create density map')
    translation = [[1, 0, 0, 0], [0, 1, 0, -1], [0, 0, 1, -1], [0, 0, 0, 1]]
    sl = []
    for s in inStruct['curveSegCell']:
        s = s[0]
        s = nibabel.affines.apply_affine(translation, s)
        s = nibabel.affines.apply_affine(scaling, s)  # scaling pas obligatoire seulement reorient => affine=np.eye(4) pour density map
        sl.append(s)
    dm = utils.density_map(sl, mask.shape, affine=numpy.diag([voxel_size[0], voxel_size[1], voxel_size[2], 1]))
    nibabel.save(nibabel.Nifti1Image(dm.astype(numpy.float32), mask_affine), self.density_map.fullPath())
    context.write('density map saved !')
