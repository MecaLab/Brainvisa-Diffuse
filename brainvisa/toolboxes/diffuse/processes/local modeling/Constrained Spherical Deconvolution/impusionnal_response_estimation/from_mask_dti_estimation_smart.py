
from brainvisa.processes import *
from brainvisa.diffuse.tools import vol_to_array, array_to_vol, array_to_mask,max_shell,is_multi_shell,shells,select_outer_shell
from dipy.reconst.dti import TensorFit
from soma import aims
import numpy as np
from joblib import load, dump
from dipy.reconst.csdeconv import response_from_mask


userLevel = 3
#roles = ('',)
name = 'Fiber Impulsionnal Response DTI Estimation (Experimental)'
category = 'Local_modeling'

signature = Signature(
	'tensor_coefficients', ReadDiskItem(
        'Diffusion Tensor Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'tensor_model', ReadDiskItem(
        'Diffusion Tensor Model',
        'Joblib Pickle file'
    ),
	'mask', ReadDiskItem(
		'Diffusion MR Mask',
		'Aims readable volume formats'
	),
	'response', WriteDiskItem(
		'Single Fiber Response',
		'Joblib Pickle File'
	),

)






def initialization ( self ):


	#linking
	self.addLink('tensor_model','tensor_coefficients')
	self.addLink('mask','tensor_coefficients')
	self.addLink('response','tensor_coefficients')

	pass



def execution( self , context ):
	#loading light objects first


	tensor_coefficients_vol = aims.read(self.tensor_coefficients.fullPath())
	tensor_coefficients = np.asarray(tensor_coefficients_vol)
	tensor_model = load(self.tensor_model.fullPath())

	tensorfit = TensorFit(tensor_model,tensor_coefficients)

	mask = vol_to_array(mask_vol)
	mask = array_to_mask(mask)

	if is_multi_shell(gtab):
		context.warning("The DWI scheme for this data is multishell: bvalues", shells(gtab),
					". CSD implementation used in Diffuse currently only handle single shell DWI scheme. By default the higher shell bval",
						max_shell(gtab), " is selected")
		context.warning("Even if only the outer shell is use for deconvolution, the following estimation method will use the full DWI scheme for response estimation. It might be inaccurate  if the deconvolved shell bvalue is too high (b5000)")




	vol = aims.read(self.diffusion_data.fullPath())
	data = np.asarray(vol)
	response,ratio = response_from_mask(gtab,data,mask)

	dump(response, self.response.fullPath())






