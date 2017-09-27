from brainvisa.processes import *
import os

def dicom_to_nifti(indir, mricron, context):
    if mricron=='dcm2niix':
        script_path = os.path.dirname(os.path.abspath(__file__))
        cmd = [ script_path + '/dcm2niix', '-z', 'y', '-f', 'data', indir ]
        context.system( *cmd ) # output directory cannot be chosen in dcm2niix
    else:
        prog = distutils.spawn.find_executable('dcm2nii')
        context.system(prog, '-f', 'y', '-d', 'n', '-e', 'n', '-p', 'n', '-i', 'n', indir)
    
