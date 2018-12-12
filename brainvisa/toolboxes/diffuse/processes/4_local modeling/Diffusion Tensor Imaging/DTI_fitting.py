# -*-coding: utf-8 -*-
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
from brainvisa.diffuse.tools import array_to_vol, array_to_mask, vol_to_array
from soma import aims
import numpy as np
from joblib import load





userLevel = 0

name = 'Diffusion Tensor Imaging (DTI) Fitting'



signature = Signature(
    'diffusion_data', ReadDiskItem(
        'Corrected DW Diffusion MR',
        'Aims readable volume formats'
    ),
    'tensor_model', ReadDiskItem(
            'Diffusion Tensor Model',
            'Joblib Pickle file'
    ),
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
    'tensor_coefficients', WriteDiskItem(
        'Diffusion Tensor Coefficients',
        'gz compressed NIFTI-1 image'
    ),
)



def initialization( self ):

    self.setOptional('mask')
    self.addLink('tensor_model','diffusion_data')
    self.addLink('mask','diffusion_data')
    self.addLink('tensor_coefficients', 'tensor_model')


def execution(self, context):

    context.write("Loading input files")
    data_vol = aims.read(self.diffusion_data.fullPath())
    hdr =data_vol.header()
    data = vol_to_array(data_vol)
    del data_vol
    if self.mask is not None:
       mask_vol= aims.read(self.mask.fullPath())
       mask = vol_to_array(mask_vol)
       del mask_vol
       mask = array_to_mask(mask)
    else:
        mask = self.mask
    tensor = load(self.tensor_model.fullPath())
    context.write("Input files loaded successfully")

    context.write("Fitting Diffusion Tensor model on data...it migh take some time")
    tenfit = tensor.fit(data, mask=mask)
    context.write("Diffusion Tensor Model fitted successfully")

    tensor_coefficients = tenfit.model_params
    vol_tensor = array_to_vol(tensor_coefficients, header=hdr)
    context.write('Writing coefficient volume on disk')
    aims.write(vol_tensor, self.tensor_coefficients.fullPath())

    #saving other metadata
    self.tensor_coefficients.setMinf('model_uuid', self.tensor_model.uuid())
    self.tensor_coefficients.setMinf('data_uuid', self.diffusion_data.uuid())
    try:
        assert self.mask is not None
        self.tensor_coefficients.setMinf('mask_uuid', self.mask.uuid())
    except Exception:
        self.tensor_coefficients.setMinf('mask_uuid', 'None')

    transformManager = getTransformationManager()
    transformManager.copyReferential(self.diffusion_data, self.tensor_coefficients)
    context.write("Processed Finished")
    pass








