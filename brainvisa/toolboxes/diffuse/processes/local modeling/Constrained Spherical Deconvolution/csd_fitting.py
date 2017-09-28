# -*- coding: utf-8 -*-
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
from soma import aims
import numpy as np

from registration import getTransformationManager
from joblib import load, dump
from brainvisa.diffuse.tools import array_to_vol
from copy import copy


userLevel = 0
name = 'Constrained Spherical Deconvolution (CSD) Fitting'
category = 'Separated Steps'

signature = Signature(
    'diffusion_data', ReadDiskItem(
        'Corrected DW Diffusion MR',
        'Aims readable volume formats'
    ),
    'csd_model', ReadDiskItem(
        'Constrained Spherical Deconvolution Model',
        'Joblib Pickle file'
    ),
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
    'fibre_odf_sh_coeff', WriteDiskItem(
        'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
    ),
)



def initialization(self):
    self.mask = None
    self.handling_multishell = 0
    self.setOptional('mask')
    self.addLink('csd_model','diffusion_data')
    self.addLink('mask','diffusion_data')
    self.addLink('fibre_odf_sh_coeff','csd_model')

    pass




def execution(self, context):

    #Load light objects first
    csd = load(self.csd_model.fullPath())

    dmri_vol = aims.read(self.diffusion_data.fullPath())
    header = dmri_vol.header()
    data = np.asarray(dmri_vol)


    if self.mask is not None:
        mask_vol = aims.read(self.mask.fullPath())
        mask_arr = np.array(mask_vol, copy=True)
        mask = mask_arr[...,0]
        if data.shape[:-1]!=mask.shape:
            raise ValueError('Diffusion data and mask used do not have the same shape')
    else:
        mask = self.mask

    csdfit = csd.fit(data, mask=mask)
    sh_coeff = csdfit.shm_coeff

    sh_coeff_volume = array_to_vol(sh_coeff, header)
    aims.write(sh_coeff_volume, self.fibre_odf_sh_coeff.fullPath())
    transformManager = getTransformationManager()
    transformManager.copyReferential(self.diffusion_data, self.fibre_odf_sh_coeff)




    pass
