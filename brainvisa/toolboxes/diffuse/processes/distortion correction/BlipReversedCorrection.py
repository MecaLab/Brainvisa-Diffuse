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

    from distutils.spawn import find_executable as find_exec
    configuration = Application().configuration
    #fsldir = configuration.FSL.fsldir
    #check for eddy implementations (two for fsl>5.0.10)
    eddy_cpu = find_exec('eddy_openmp')
    #pb ! executable can exist even if no GPU on the system (dont consider GPU for now)
    #eddy_gpu_old = os.path.join(fsldir ,'bin','eddy.gpu')
    #eddy_gpu_new = find_exec('eddy_cuda')
    eddy_base = find_exec('eddy')
    #For now we consider that there is a problem if no CPU implementation of eddy  is found
    if eddy_cpu is None and eddy_base is None:
        raise ValidationError(_t_('NO CPU implementation of eddy was found ! Check fsldir and fsl_command_prefix values into Brainvisa Preferences FSL menu !'))
    cmds = ['fslmaths','fslroi','fsl_anat','fslmerge','topup','applytopup']
    for cmd in cmds:
        if not find_exec(configuration.FSL.fsl_commands_prefix + cmd):
            raise ValidationError(_t_(' FSL ' + cmd + ' commandline could not be found. Check fsldir and fsl_command_prefix values into Brainvisa Preferences FSL menu !'))
    pass

from brainvisa.processes import *
from soma.wip.application.api import Application
from brainvisa.registration import getTransformationManager
from brainvisa.diffuse import BrainExtraction
from distutils.spawn import find_executable
from copy import copy
import numpy
import time

name = 'Blip-reversed based correction'
userLevel = 0

## Readout time (in sec)

signature=Signature(
  'dwi_data', ReadDiskItem( 'Raw Denoised Diffusion MR', 'Aims readable volume formats' ),
  'bvals', ReadDiskItem( 'Raw B Values', 'Text file' ),
  'bvecs', ReadDiskItem( 'Reoriented B Vectors', 'Text file' ),
  'blip_reversed_data', ReadDiskItem( 'Blip Reversed DW Diffusion MR', 'Aims readable volume formats' ),

  'phase_encoding_direction', Choice( "AP", "PA", "LR", "RL" ),
  # 'phase_encoding_scheme', Choice( "AP", "PA", "AP+PA", "LR", "RL", "LR+RL" ),
  'readout_time', Number(),
  'entire_sphere_sampling', Boolean(),
  'multi_shell', Boolean(),
  'b0_bias_correction', Boolean(),
  'flm', Choice( "quadratic", "linear", "cubic" ),
  'fwhm', Number(),
  'niter', Number(),
  'nvoxhp', Number(),
  'brain_extraction_factor', Number(),

  'dwi_unwarped', WriteDiskItem( 'Unwarped DW Diffusion MR', 'gz compressed NIFTI-1 image' ),
  'topup_parameters', WriteDiskItem( 'Blip Reversed Parameters', 'Text file' ),
  'topup_index', WriteDiskItem( 'Blip Reversed Index', 'Text file' ),
  'topup_data', WriteDiskItem( 'Blip Reversed Data', 'gz compressed NIFTI-1 image' ),
  'topup_bvals', WriteDiskItem( 'Blip Reversed B Values', 'Text file' ),
  'topup_bvecs', WriteDiskItem( 'Blip Reversed B Vectors', 'Text file' ),
  'topup_b0_volumes', WriteDiskItem( 'Blip Reversed B0 Volumes', 'gz compressed NIFTI-1 image' ),
  'topup_b0_volumes_unwarped', WriteDiskItem( 'Blip Reversed Unwarped B0 Volumes', 'gz compressed NIFTI-1 image' ),
  'topup_b0_mean', WriteDiskItem( 'Blip Reversed B0 Mean', 'gz compressed NIFTI-1 image' ),
  'topup_b0_mean_brain', WriteDiskItem( 'Blip Reversed B0 Mean Brain', 'gz compressed NIFTI-1 image' ),
  'topup_b0_mean_brain_mask', WriteDiskItem( 'Blip Reversed B0 Mean Mask', 'gz compressed NIFTI-1 image' ),
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
    self.b0_bias_correction = False
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
    self.linkParameters( 'blip_reversed_data', 'dwi_data' )
    self.linkParameters( 'dwi_unwarped', 'dwi_data', self.linkOutput)
    self.linkParameters( 'topup_parameters', 'dwi_unwarped' )
    self.linkParameters( 'topup_index', 'dwi_unwarped' )
    self.linkParameters( 'topup_data', 'dwi_unwarped' )
    self.linkParameters( 'topup_bvals', 'dwi_unwarped' )
    self.linkParameters( 'topup_bvecs', 'dwi_unwarped' )
    self.linkParameters( 'topup_b0_volumes', 'dwi_unwarped' )
    self.linkParameters( 'topup_b0_volumes_unwarped', 'dwi_unwarped' )
    self.linkParameters( 'topup_b0_mean', 'dwi_unwarped' )
    self.linkParameters( 'topup_b0_mean_brain', 'dwi_unwarped' )
    self.linkParameters( 'topup_b0_mean_brain_mask', 'dwi_unwarped' )
    self.linkParameters( 'corrected_bvecs', 'dwi_unwarped' )

def execution( self, context ):
  
    context.write('Distortion correction using blip-reversed images')
    configuration = Application().configuration
    fsldir = configuration.FSL.fsldir
    FSL_topup_directory = os.path.dirname(self.topup_b0_volumes.fullPath())
    tmp_directory = configuration.brainvisa.temporaryDirectory

    context.write('- Reading data')
    up_img = aims.read(self.dwi_data.fullPath())
    up_data = up_img.arraydata()
    up_bvals = numpy.loadtxt(self.bvals.fullPath())
    up_bvecs = numpy.loadtxt(self.bvecs.fullPath())
    context.write(up_bvals.shape)
    context.write(up_bvecs.shape)
    down_img = aims.read(self.blip_reversed_data.fullPath())
    down_data = down_img.arraydata()
    Nvol_up = self.dwi_data.get('volume_dimension', search_header=True)[3]
    Nvol_down = self.blip_reversed_data.get('volume_dimension', search_header=True)[3]
    if Nvol_up == Nvol_down:
        blip_down_scheme = 'full_sequence'
        context.write('Full acquisition with opposite phase-encode direction DETECTED')
    else:
        blip_down_scheme = 'b0_volumes_only'
        context.write('Only b0 volumes with opposite phase-encode direction DETECTED')

    context.write('- Correcting number of slices')
    dimx = self.dwi_data.get( 'volume_dimension', search_header=True )[0]
    dimy = self.dwi_data.get( 'volume_dimension', search_header=True )[1]
    dimz = self.dwi_data.get( 'volume_dimension', search_header=True )[2]
    if dimz % 2 != 0:
       context.write('ODD number of slices')
       up_data = up_data[:,1:,:,:]
       down_data = down_data[:,1:,:,:]
       dimz = dimz -1

    context.write('- b0 volumes extraction')
    up_b0_index = numpy.where(up_bvals < 50)[0] ## bvals==0 not possible when bvalues take values +-5 or +-10
    ##    if len(up_b0_index)>3:
    ##        up_b0_index=up_b0_index[::2]
    up_b0 = up_data[up_b0_index, :, :, :]
    if blip_down_scheme == 'b0_volumes_only':
       down_bvals = numpy.zeros((1, Nvol_down))+up_bvals[up_b0_index[0]]
       down_bvals = down_bvals[0]
       down_b0_index = numpy.arange(Nvol_down)
       down_bvecs = numpy.zeros((3, Nvol_down))+up_bvecs[:,up_b0_index[0]].reshape((3,1))
    else:
       down_bvals = up_bvals
       down_b0_index = up_b0_index
       down_bvecs = up_bvecs

    down_b0 = down_data[down_b0_index, :, :, :]

    context.write('- Merging blip-up and blip-down b0 images')
    up_down_b0 = numpy.concatenate((up_b0, down_b0))
    up_down_b0_vol = aims.Volume(up_down_b0)
    up_down_b0_vol.copyHeaderFrom(up_img.header())
    aims.write(up_down_b0_vol, self.topup_b0_volumes.fullPath())

    if self.b0_bias_correction:
       context.write('- Intensity bias correction of b0 images')
       biais_corrected_img = context.temporary('gz compressed NIFTI-1 image' )
       sec = int(time.time())
       for i in range(len(up_b0_index)+len(down_b0_index)):
           context.write('volume '+str(i))
           context.system( configuration.FSL.fsl_commands_prefix + 'fslroi', self.topup_b0_volumes.fullPath(), tmp_directory+'/bias_img_'+str(sec)+'.nii.gz', str(i), '1' )
           context.system( configuration.FSL.fsl_commands_prefix + 'fsl_anat', '--noreorient', '--nocrop', '--noreg', '--nononlinreg', '--noseg', '--nosubcortseg', '-t', 'T2', '-i', tmp_directory+'/bias_img_'+str(sec)+'.nii.gz')
           if i==0:
               context.system( 'cp', tmp_directory + '/bias_img_'+str(sec)+'.anat/T2_biascorr.nii.gz', biais_corrected_img.fullPath())
           else:
               context.system( configuration.FSL.fsl_commands_prefix + 'fslmerge', '-t', biais_corrected_img.fullPath(), biais_corrected_img.fullPath(), tmp_directory + '/bias_img_'+str(sec)+'.anat/T2_biascorr.nii.gz')
           context.system( 'rm', '-r', tmp_directory + '/bias_img_'+str(sec)+'.anat/' )
       context.system( 'mv', biais_corrected_img.fullPath(), self.topup_b0_volumes.fullPath())

    context.write('- Merging blip-up and blip-down dwi images')
    ##    context.system( configuration.FSL.fsl_commands_prefix + 'fslmerge', '-t', self.topup_data.fullPath(), self.dwi_data.fullPath(), self.blip_reversed_data.fullPath() )
    up_down_data = numpy.concatenate((up_data, down_data))
    up_down_data_vol = aims.Volume(up_down_data)
    up_down_data_vol.copyHeaderFrom(up_img.header())
    aims.write(up_down_data_vol, self.topup_data.fullPath())
    context.write('- Merging bvals and bvecs')
    up_down_bvals = numpy.concatenate((up_bvals, down_bvals), axis=0)
    up_down_bvals = up_down_bvals.reshape((1,len(up_down_bvals)))
    numpy.savetxt(self.topup_bvals.fullPath(), up_down_bvals, fmt='%d')
    up_down_bvecs = numpy.concatenate((up_bvecs, down_bvecs), axis=1)
    up_down_bvecs = up_down_bvecs
    numpy.savetxt(self.topup_bvecs.fullPath(), up_down_bvecs, fmt='%.15f')

    context.write('- Setting acquisition parameters')
    PE_parameters = self.topup_parameters.fullPath()
    PE_index = self.topup_index.fullPath()
    f_param = open(PE_parameters, 'w')
    f_index = open(PE_index, 'w')
    PE_list = ["AP", "PA", "LR", "RL"]
    vector_list_up = ['0 1 0 ', '0 -1 0 ', '1 0 0 ', '-1 0 0 ']
    vector_list_down = ['0 -1 0 ', '0 1 0 ', '-1 0 0 ', '1 0 0 ']
    indx = PE_list.index(self.phase_encoding_direction)
    [f_param.write(vector_list_up[indx] + str(self.readout_time) + '\n') for i in range(len(up_b0_index))]
    [f_param.write(vector_list_down[indx] + str(self.readout_time) + '\n') for i in range(len(down_b0_index))]
    val=1
    for i in range(len(up_data)+len(down_data)):
       if i in up_b0_index[1:] or i in down_b0_index+len(up_bvals):
           val+=1
       f_index.write(str(val)+' ')
    f_param.close()
    f_index.close()

    context.write('- Estimation of the susceptibility off-resonance field...')
    topup_config = fsldir + '/etc/flirtsch/b02b0.cnf'
    cmd = [ configuration.FSL.fsl_commands_prefix + 'topup', '--imain=' + self.topup_b0_volumes.fullPath(), '--datain=' + self.topup_parameters.fullPath(), '--config=' + topup_config, '--out=' + FSL_topup_directory+ '/topup', '--iout=' + self.topup_b0_volumes_unwarped.fullPath(), '--verbose' ]
    context.system( *cmd )

    context.write('- Apply fieldcoeff to b0 volumes')
    up_b01 = context.temporary('gz compressed NIFTI-1 image' )
    down_b01 = context.temporary('gz compressed NIFTI-1 image' )
    up_b01_vol = aims.Volume(up_b0[0,:,:,:])
    up_b01_vol.copyHeaderFrom(up_img.header())
    aims.write(up_b01_vol, up_b01.fullPath())
    down_b01_vol = aims.Volume(down_b0[0,:,:,:])
    down_b01_vol.copyHeaderFrom(down_img.header())
    aims.write(down_b01_vol, down_b01.fullPath())
    cmd = [ configuration.FSL.fsl_commands_prefix + 'applytopup', '--imain=' + up_b01.fullPath() + ',' + down_b01.fullPath(), '--inindex='+ '1' + ',' + str(len(up_b0_index)+1), '--datain=' + self.topup_parameters.fullPath(), '--topup=' + FSL_topup_directory + '/topup', '--out=' + self.topup_b0_mean.fullPath()]
    context.system( *cmd )
    BrainExtraction.defaultBrainExtraction(self.topup_b0_mean.fullPath(), self.topup_b0_mean_brain.fullPath(), f=str(self.brain_extraction_factor))

    context.write('- Eddy current estimation and correction... [can take several hours]')
    memoryUse = 2*8*(len(up_data)+len(down_data))*dimx*dimy*dimz/1000000
    context.write('Estimated memory usage: '+str(memoryUse)+' MB')

    # if oldORnew == "old":
    #    context.write('INFO: FSL version is anterior to 5.0.9')
    #    eddyExec = fsldir + '/bin/eddy.gpu'
    # else:
    #    context.write('INFO: FSL version is 5.0.9 or newer')
    #    eddyExec = fsldir + '/bin/eddy_cuda'
    eddyExec = find_executable('eddy_openmp')
    if eddyExec:
       context.write('CPU-multithread version of eddy found')
    else:
       context.write('CPU/GPU-multithread version of eddy NOT found')
       eddyExec = find_executable('eddy')
    #else:
        #eddyExec = fsldir + '/bin/eddy.gpu'
        #if os.path.isfile(eddyExec) == True:
           # context.write('GPU-multithread version of eddy found')
        #else:
           # eddyExec = fsldir + '/bin/eddy_cuda'
            #if os.path.isfile(eddyExec) == True:
               # context.write('GPU-multithread version of eddy found')
            #else:
             #   context.write('CPU/GPU-multithread version of eddy NOT found')
              #  eddyExec = fsldir + '/bin/eddy'

    ## default parameters for eddy
    #--fep # Fill Empty Planes by duplication or interpolation, can occur depending on scanner
    #--dont_peas # Post-Eddy-Alignment of Shell. To use only if single shell acquisition
    #--data_is_shelled # To use only if multi-shell, to force uncheck in case of special acquisition with "mini-shell" (a few dir with low bval)
    #--dont_sep_offs_move # should not be used
    #--interp = "spline" # interpolation model used during estimation phase and final resampling, use default
    #--ff = "10" # cannot be higher than default 10, safe value
    if self.entire_sphere_sampling == False or Nvol_up < 60:
       slm = "linear"
    else:
       slm = "none"
    if blip_down_scheme == 'b0_volumes_only':
       resamp = "jac"
    else:
       resamp = "lsr"
    cmd1 = '. ' + fsldir + '/etc/fslconf/fsl.sh'
    cmd2 = eddyExec + ' --imain=' + self.topup_data.fullPath() + ' --mask=' + self.topup_b0_mean_brain_mask.fullPath() + ' --acqp=' + self.topup_parameters.fullPath() + ' --index=' + self.topup_index.fullPath() + ' --bvecs=' + self.topup_bvecs.fullPath() + ' --bvals=' + self.topup_bvals.fullPath() + ' --topup=' + FSL_topup_directory + '/topup' + ' --out=' + FSL_topup_directory + '/topup_eddy'
    cmd2 += ' --flm=' + str(self.flm) + ' --slm=' + slm+ ' --fwhm=' + str(self.fwhm) + ',0,0,0,0' + ' --niter=' + str(self.niter) + ' --fep --interp=spline --resamp=' + resamp + ' --nvoxhp=' + str(self.nvoxhp) + ' --ff=10 --very_verbose'
    if not self.multi_shell:
       cmd2 += " --dont_peas"
    else:
        cmd2 += " --data_is_shelled" # option does NOT exist
    cmd = cmd1 + ' ; ' + cmd2
    os.system( cmd )

    context.write('- Save corrected images and bvecs')
    context.system( configuration.FSL.fsl_commands_prefix + 'fslmaths', FSL_topup_directory + '/topup_eddy.nii.gz', '-abs', '-uthr', '65535', FSL_topup_directory + '/topup_eddy.nii.gz' ) # manage pb of type FLOAT and negative values become infinite values, data from Centre IRMf are in U16 [0,65535]
    context.write('threshold')
    if blip_down_scheme == 'b0_volumes_only':
        context.system( configuration.FSL.fsl_commands_prefix + 'fslroi', FSL_topup_directory + '/topup_eddy.nii.gz', self.dwi_unwarped.fullPath(), 0, str(len(up_bvals)) )
    else:
        context.system( 'cp', FSL_topup_directory + '/topup_eddy.nii.gz', self.dwi_unwarped.fullPath())
    new_bvecs = numpy.loadtxt(FSL_topup_directory + '/topup_eddy.eddy_rotated_bvecs')
    new_bvecs = new_bvecs[:,:up_bvecs.shape[1]]
    numpy.savetxt(self.corrected_bvecs.fullPath(), new_bvecs, fmt='%.15f')

    transformManager = getTransformationManager()
    transformManager.copyReferential( self.dwi_data, self.dwi_unwarped )

    context.write('Finished')


