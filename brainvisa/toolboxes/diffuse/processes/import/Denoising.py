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

# The LPCA filter is described in:                                       *
# *                                                                        *
# * J. V. Manjon, P. Coupe, L. Concha, A. Buades, D. L. Collins, M. Robles *
# * Diffusion Weighted Image Denoising using overcomplete Local PCA.       *
# * PLoS ONE 8(9): e73021. 

from brainvisa.processes import *
from soma.wip.application.api import Application
from brainvisa.registration import getTransformationManager
import numpy
import os


name = 'Denoising LPCA'
userLevel = 0

signature=Signature(
    'denoisingPackage', ReadDiskItem('Directory', 'Directory'),
    'dwi_data', ReadDiskItem( 'Raw Diffusion MR', 'Aims readable volume formats' ),
    'bvecs', ReadDiskItem( 'Reoriented B Vectors', 'Text file' ),
    'method', Choice("Local PCA", "Optimized NLM", "Adaptative ONLM", "Multi-resolution ONLM", "Oracle DCT", "Prefiltered rationally invariant NLM"),
    'rician', Boolean(),
    'denoised_dwi_data', WriteDiskItem( 'Denoised Diffusion MR', 'gz compressed NIFTI-1 image' ),
)

def initialization( self ):
  self.linkParameters( 'denoised_dwi_data', 'dwi_data' )
  self.linkParameters( 'bvecs', 'dwi_data' )
  self.method = "Local PCA"
  self.rician = False
  self.denoisingPackage = '/hpc/soft/matlab_tools/dwi_denoising/DWIDenoisingPackage_r01_pcode/DWIDenoisingPackage' #'/hpc/meca/users/brun.l/scripts/DWIDenoisingPackage_r01_pcode/DWIDenoisingPackage'
  
def execution( self, context ):

    configuration = Application().configuration
    tmpdir = configuration.brainvisa.temporaryDirectory
    spm = configuration.SPM.spm12_path
    if spm is None:
        spm = configuration.SPM.spm8_path
    matlab_exe = configuration.matlab.executable

    context.system( 'cp', self.dwi_data, tmpdir + '/infile.nii.gz' )
    context.system('gunzip', '-f', tmpdir + '/infile.nii.gz')
    context.write('Denoising...')

    bvec = numpy.loadtxt(self.bvecs.fullPath())

    if self.method != "Local PCA":
        patchradius = 1
        context.write('patch size: ', 2*patchradius+1, 'x', 2*patchradius+1, 'x', 2*patchradius+1, 'voxels')
    if self.rician == 1:
        context.write('Rician noise model')
    else:
        context.write('Gaussian noise model')

    matfilepath = tmpdir + '/denfile.m' #context.temporary( 'Matlab script' )
    matfile = file(matfilepath,'w')
    matfile.write("addpath('%s');\n" % (spm))
    matfile.write("addpath(genpath('%s'));\n" % (self.denoisingPackage))
    matfile.write("namein = '%s';\n" % (tmpdir + '/infile.nii'))
    matfile.write("nameout = '%s';\n" % (tmpdir + '/outfile.nii'))
    matfile.write("rician=%d;\n" % (int(self.rician)))
    matfile.write("verbose=1;\n")
    matfile.write("beta=1;\n")
    matfile.write("searchradius=3;\n")
    matfile.write("nbthread=1;\n")
    matfile.write("dir = load('%s');\n" % (self.bvecs.fullPath()))
    matfile.write("dir=transpose(dir);\n")

    matfile.write("VI=spm_vol(namein);\n")
    matfile.write("ima=spm_read_vols(VI);\n")
    matfile.write("s=size(ima);\n")
    matfile.write("ima = double(ima);\n")
    matfile.write("map = isnan(ima(:));\n")
    matfile.write("ima(map) = 0;\n")
    matfile.write("map = isinf(ima(:));\n")
    matfile.write("ima(map) = 0;\n")
    matfile.write("mini = min(ima(:));\n")
    matfile.write("ima = ima - mini;\n")
    matfile.write("maxi=max(ima(:));\n")
    matfile.write("ima=ima*255/maxi;\n")
    if self.method != "Adaptative ONLM" and self.method != "Local PCA":
        matfile.write("[hfinal, hvect, nbB0, hobj, hbg] = DWINoiseEstimation(ima, dir, rician, verbose);\n")
        matfile.write("if(isnan(hfinal))\n")
        matfile.write("\tdisp('error during noise estimation');\n")
        matfile.write("end\n")
    if self.method == "Optimized NLM":
        matfile.write("DWIdenoised = DWIDenoisingORNLM(ima, hfinal, beta, patchradius, 5, rician, nbthread, verbose);\n")
    elif self.method == "Adaptative ONLM":
        matfile.write("DWIdenoised = DWIDenoisingAONLM(ima,patchradius, 3, beta , rician, nbthread, verbose);\n")
    elif self.method == "Multi-resolution ONLM":
        matfile.write("DWIdenoised = DWIDenoisingORNLMMultires(ima, dir, hfinal, beta, patchradius, 3, rician, nbthread, verbose);\n")
    elif self.method == "Oracle DCT":
        matfile.write("DWIdenoised = DWIDenoisingODCT(ima, hfinal, beta, rician, nbthread, verbose);\n")
    elif self.method == "Prefiltered rationally invariant NLM":
        matfile.write("DWIdenoised = DWIDenoisingPRINLM(ima, hfinal, beta, rician, nbthread, verbose);\n")
    elif self.method == "Local PCA":
        matfile.write("DWIdenoised = DWIDenoisingLPCA(ima, beta, rician, nbthread, verbose);\n")
    matfile.write("DWIdenoised=DWIdenoised*maxi/255 + mini;\n")
    matfile.write("map = find(DWIdenoised<0);\n")
    matfile.write("DWIdenoised(map) =0;\n")
    matfile.write("map = isnan(DWIdenoised);\n")
    matfile.write("DWIdenoised(map)=0;\n")
    matfile.write("VO = VI;\n")
    matfile.write("for i=1:s(4)\n")
    matfile.write("VO(i).dim=s(1:3);\n")
    matfile.write("VO(i).fname = nameout;\n")
    matfile.write("spm_write_vol(VO(i),DWIdenoised(:,:,:,i));\n")
    matfile.write("end\n")
    matfile.write("disp('Filtering done');\n")
    matfile.write("exit\n")
    matfile.close()
    os.system(matlab_exe + ' -nodisplay -r "run %s"' % (matfilepath)) # -nodisplay -nodesktop # the scripts plot some figures :(

    context.system('gzip', tmpdir + '/outfile.nii')
    context.system('mv', tmpdir + '/outfile.nii.gz', self.denoised_dwi_data)
    context.system( 'rm', tmpdir + '/infile.nii' )
    transformManager = getTransformationManager()
    transformManager.copyReferential( self.dwi_data, self.denoised_dwi_data )
    context.write('Finished')

