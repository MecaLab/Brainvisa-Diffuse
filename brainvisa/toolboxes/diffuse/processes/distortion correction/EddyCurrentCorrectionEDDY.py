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
from brainvisa.diffuse import BrainExtraction
from brainvisa.registration import getTransformationManager
from distutils.spawn import find_executable
import numpy

name = 'Motion and Eddy-current correction (FSL-Eddy)'
userLevel = 0

signature=Signature(
  'dwi_data', ReadDiskItem( 'Raw Denoised Diffusion MR', 'Aims readable volume formats' ),
  'bvals', ReadDiskItem( 'Raw B Values', 'Text file' ),
  'bvecs', ReadDiskItem( 'Reoriented B Vectors', 'Text file' ),
  'readout_time', Number(),
  'phase_encoding_direction', Choice( "AP", "PA", "LR", "RL" ),
  'entire_sphere_sampling', Boolean(),
  'multi_shell', Boolean(),
  'flm', Choice( "quadratic", "linear", "cubic" ),
  'fwhm', Number(),
  'niter', Number(),
  'nvoxhp', Number(),
  'brain_extraction_factor', Number(),

  'dwi_eddy_corrected', WriteDiskItem( 'EC corrected DW Diffusion MR', 'gz compressed NIFTI-1 image' ),
  'eddy_parameters', WriteDiskItem( 'Blip Reversed Parameters', 'Text file' ),
  'eddy_index', WriteDiskItem( 'Blip Reversed Index', 'Text file' ),
  'eddy_b0_volumes', WriteDiskItem( 'Blip Reversed B0 Volumes', 'gz compressed NIFTI-1 image' ),
  'eddy_b0_mean', WriteDiskItem( 'Blip Reversed B0 Mean', 'gz compressed NIFTI-1 image' ),
  'eddy_b0_mean_brain', WriteDiskItem( 'Blip Reversed B0 Mean Brain', 'gz compressed NIFTI-1 image' ),
  'eddy_b0_mean_brain_mask', WriteDiskItem( 'Blip Reversed B0 Mean Mask', 'gz compressed NIFTI-1 image' ),
  'corrected_bvecs', WriteDiskItem( 'Corrected B Vectors', 'Text file' ),
)

def linkOutput(self, proc, dummy):
    required = {}
    required['center'] = self.dwi_data.get('center')
    required['subject'] = self.dwi_data.get('subject')
    required['acquisition'] = self.dwi_data.get('acquisition')
    return self.signature['dwi_unwarped'].findValue(self.dwi_data, requiredAttributes=required)

def initialization( self ):
    self.entire_sphere_sampling = True
    self.multi_shell = False
    self.flm = "quadratic" # default. Works better on HCP than linear
    self.fwhm = "0" # if substancial mvt, eddy fails to converge in 5 iter, use "10,0,0,0,0"
    self.niter = "5" # NB: eddy do not check for convergence
    self.nvoxhp = "1000" # for 2x2x2mm resolution or lower. For higher resolution and GPU use, increase this number
    self.brain_extraction_factor = 0.2
    self.setOptional('flm')
    self.setOptional('fwhm')
    self.setOptional('niter')
    self.setOptional('nvoxhp')
    self.setOptional('brain_extraction_factor')
    self.linkParameters( 'bvals', 'dwi_data' )
    self.linkParameters( 'bvecs', 'dwi_data' )
    self.linkParameters( 'dwi_eddy_corrected', 'dwi_data', self.linkOutput)
    self.linkParameters( 'eddy_parameters', 'dwi_eddy_corrected' )
    self.linkParameters( 'eddy_index', 'dwi_eddy_corrected' )
    self.linkParameters( 'eddy_b0_volumes', 'dwi_eddy_corrected' )
    self.linkParameters( 'eddy_b0_mean', 'dwi_eddy_corrected' )
    self.linkParameters( 'eddy_b0_mean_brain', 'dwi_eddy_corrected' )
    self.linkParameters( 'eddy_b0_mean_brain_mask', 'dwi_eddy_corrected' )
    self.linkParameters( 'corrected_bvecs', 'dwi_eddy_corrected' )
  
def execution( self, context ):
    
    configuration = Application().configuration

    FSL_eddy_directory = os.path.dirname(self.eddy_b0_volumes.fullPath())
    
    context.write('Setting acquisition parameters')
    img = aims.read(self.dwi_data.fullPath())
    dwi_data = img.arraydata()
    Nvol = self.dwi_data.get('volume_dimension', search_header=True)[3]
    bvals = numpy.loadtxt(self.bvals.fullPath())
    b0_index = numpy.where(bvals < 100)[0] ## bvals==0 not possible when bvalues take values +-5 or +-10
    b0_sum = dwi_data[b0_index,:,:,:]
    b0_vol = aims.Volume(b0_sum)
    b0_vol.copyHeaderFrom(img.header())
    aims.write(b0_vol, self.eddy_b0_volumes.fullPath())

    PE_parameters = self.eddy_parameters.fullPath()
    PE_index = self.eddy_index.fullPath()
    PE_list = ["AP", "PA", "LR", "RL"]
    vector_list = ['0 1 0 ', '0 -1 0 ', '1 0 0 ', '-1 0 0 ']
    indx = PE_list.index(self.phase_encoding_direction)
    f_param = open(PE_parameters, 'w')
    f_index = open(PE_index, 'w')
    [f_param.write(vector_list[indx] + str(self.readout_time) + '\n') for i in range(len(b0_index))]
    val = 1
    for i in range(len(bvals)):
        if i in b0_index[1:]:
            val += 1
        f_index.write(str(val) + ' ')
    # tmp = [f_index.write('1 ') for i in range(len(bvals))]
    f_param.close()
    f_index.close()

    context.write('Eddy current estimation and correction... [can take several hours]')
    cmd = [ configuration.FSL.fsl_commands_prefix + 'fslmaths', self.eddy_b0_volumes.fullPath(), '-Tmean', self.eddy_b0_mean.fullPath() ]
    context.system( *cmd )
    BrainExtraction.defaultBrainExtraction(self.eddy_b0_mean.fullPath(), self.eddy_b0_mean_brain.fullPath(), f=str(self.brain_extraction_factor))
    fsldir = configuration.FSL.fsldir
    eddyExec = find_executable('eddy_openmp')
    if eddyExec:
        context.write('CPU-multithread version of eddy found')
    else:
        eddyExec = fsldir + '/bin/eddy.gpu'
        if os.path.isfile(eddyExec) == True:
            context.write('GPU-multithread version of eddy found')
        else:
            eddyExec = fsldir + '/bin/eddy_cuda'
            if os.path.isfile(eddyExec) == True:
                context.write('GPU-multithread version of eddy found')
            else:
                context.write('CPU/GPU-multithread version of eddy NOT found')
                eddyExec = fsldir + '/bin/eddy'
    if self.entire_sphere_sampling == False or Nvol < 60:
        if Nvol < 30:
            context.write('WARNING: For eddy to work well, data should contain more than 30 directions!')
        slm = "linear"
    else:
        slm = "none"
    cmd1 = '. ' + fsldir + '/etc/fslconf/fsl.sh'
    cmd2 = eddyExec + ' --imain=' + self.dwi_data.fullPath() + ' --mask=' + self.eddy_b0_mean_brain_mask.fullPath() + ' --acqp=' + self.eddy_parameters.fullPath() + ' --index=' + self.eddy_index.fullPath() + ' --bvecs=' + self.bvecs.fullPath() + ' --bvals=' + self.bvals.fullPath() + ' --out=' + FSL_eddy_directory + '/eddy'
    cmd2 += ' --flm=' + str(self.flm) + ' --slm=' + slm + ' --fwhm=' + str(self.fwhm) + ',0,0,0,0' + ' --niter=' + str(self.niter) + ' --fep --interp=spline --resamp=jac --nvoxhp=' + str(self.nvoxhp) + ' --ff=10 --very_verbose'
    if not self.multi_shell:
        cmd2 += " --dont_peas"
    ##    else:
    ##        cmd2 += " --data_is_shelled" # option does NOT exist
    cmd = cmd1 + ' ; ' + cmd2
    os.system( cmd )

    context.system(configuration.FSL.fsl_commands_prefix + 'fslmaths', FSL_eddy_directory + '/eddy.nii.gz', '-abs', self.dwi_eddy_corrected.fullPath())  # remove negative values
    shutil.copy2(FSL_eddy_directory + '/eddy.eddy_rotated_bvecs', self.corrected_bvecs.fullPath())
    
    transformManager = getTransformationManager()
    transformManager.copyReferential( self.dwi_data, self.dwi_eddy_corrected )

    context.write('Finished')
