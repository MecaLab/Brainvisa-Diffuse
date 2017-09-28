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
# # knowledge of the CeCILL license version 2 and that you accept its terms.



from brainvisa.processes import *
from brainvisa.registration import getTransformationManager
from brainvisa.diffuse.tools import array_to_vol, vol_to_array
from dipy.reconst.dti import TensorFit
from joblib import load
from soma import aims
import numpy as np



userLevel = 0
name = 'Diffusion Tensor Imaging (DTI) Signal Prediction'


signature = Signature(
    'tensor_coefficients', ReadDiskItem(
        'Diffusion Tensor Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'tensor_model',ReadDiskItem(
        'Diffusion Tensor Model',
        'Joblib Pickle file'
    ),
    'S0_signal', ReadDiskItem(
        'B0 Volume Brain',
        'gz compressed NIFTI-1 image'
    ),
    'predicted_signal', WriteDiskItem(
        'DTI Predicted Signal',
        'gz compressed NIFTI-1 image'
    ),
)



def initialization(self):
    self.addLink('tensor_model','tensor_coefficients')
    self.addLink('S0_signal', 'tensor_model' )
    self.addLink('predicted_signal','tensor_coefficients')
    pass




def execution(self, context):

    tensor_coeff = aims.read(self.tensor_coefficients.fullPath())
    tensor_params = np.asarray(tensor_coeff)
    tensor_model = load(self.tensor_model.fullPath())
    gtab = tensor_model.gtab
    #Loading base signal
    S0 = aims.read(self.S0_signal.fullPath())
    S0 = vol_to_array(S0)

    tenfit = TensorFit(tensor_model,tensor_params)
    pred_sign = tenfit.predict(gtab=gtab,S0=S0)
    hdr = tensor_coeff.header()
    pred_vol = array_to_vol(pred_sign, header=hdr)
    aims.write(pred_vol,self.predicted_signal.fullPath())

    #Handling metada
    transformManager = getTransformationManager()
    transformManager.copyReferential(self.predicted_signal, self.tensor_coefficients)

    context.write("Process finish successfully")
    pass
