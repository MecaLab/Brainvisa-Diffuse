from brainvisa.processes import *
import os
import glob
from distutils.spawn import find_executable

def dicom_to_nifti(indir, outdir, context,filename='data', mricron='dcm2niix'):
    """
    Launch dicom to nifti conversion from Brainvisa process using either dcm2niix or dcm2nii.
    dcm2niix should be used,we only keep dcm2nii for rare case.
    :param indir:
    :param outdir:
    :param context:
    :param filename: name of the output
    :param mricron: converter program either dcm2niix or dcmnii
    :return:
    """

    converter = find_executable(mricron)
    if mricron == 'dcm2niix':
        cmd = [converter, '-z', 'y', '-f', filename, '-o', outdir, indir ]
        context.system(*cmd)
    else:
        context.system(converter, '-f', 'y', '-d', 'n', '-e', 'n', '-p', 'n', '-i', 'n', '-o', outdir, indir)
        #modify the filename so that it corresponds to what is expected

