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
from brainvisa.diffuse.tools import array_to_vol
from registration import getTransformationManager
from soma import aims
import numpy as np
from joblib import load
from dipy.reconst.csdeconv import SphHarmFit



userLevel = 0
name = 'Constrained Spherical Deconvolution (CSD) Derived Indices'
category = 'model'
signature = Signature(

    'fibre_odf_sh_coeff', ReadDiskItem(
        'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'csd_model', ReadDiskItem(
        'Constrained Spherical Deconvolution Model',
        'Joblib Pickle file'
    ),
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),

    'generalized_fractionnal_anisotropy', WriteDiskItem(
        'Generalized Fractionnal Anisotropy Volume',
        'gz compressed NIFTI-1 image',
    ),
)



def initialization(self):
    self.addLink('csd_model','fibre_odf_sh_coeff')
    self.addLink('mask','fibre_odf_sh_coeff')
    self.addLink('generalized_fractionnal_anisotropy', 'fibre_odf_sh_coeff')
    self.setOptional('mask')
    self.setHidden('csd_model')
    pass



def execution(self, context):

    csd_model = load(self.csd_model.fullPath())
    csd_coeff = aims.read(self.fibre_odf_sh_coeff.fullPath())
    h = csd_coeff.header()
    sh_coeff = np.asarray(csd_coeff)
    mask_vol = aims.read(self.mask.fullPath())
    mask = np.array(mask_vol,copy=False)[...,0].copy()
    context.write(mask.shape)


    csd_fit = SphHarmFit(csd_model,sh_coeff, mask)


    transformManager = getTransformationManager()
    # Mandatory parameters
    gfa = csd_fit.gfa
    GFA = self.array_to_vol(gfa,h)
    aims.write(GFA, self.generalized_fractionnal_anisotropy.fullPath())
    transformManager.copyReferential(self.fibre_odf_sh_coeff, self.generalized_fractionnal_anisotropy)

    pass
