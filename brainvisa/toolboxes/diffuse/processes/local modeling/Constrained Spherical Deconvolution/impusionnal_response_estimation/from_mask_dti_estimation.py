
from brainvisa.processes import *
from brainvisa.diffuse.tools import vol_to_array, array_to_vol, array_to_mask,max_shell,is_multi_shell,shells,select_outer_shell
from brainvisa.diffuse.building_spheres import read_sphere
from dipy.reconst.csdeconv import recursive_response
from dipy.core.gradients import gradient_table_from_bvals_bvecs
from copy import copy
from soma import aims
import numpy as np
from joblib import load, dump
from dipy.reconst.csdeconv import response_from_mask


userLevel = 2
#roles = ('',)
name = 'Fiber Impulsionnal Response DTI Estimation'
category = 'Local_modeling'

signature = Signature(
	'diffusion_data', ReadDiskItem(
		'Corrected DW Diffusion MR',
		'Aims readable volume formats'
	),
	'gradient_table', ReadDiskItem(
		'Gradient Table',
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
	#default dipy values
	self.sh_order = 8
	self.initial_fa = 0.08
	self.initial_trace = 0.0021
	self.peak_threshold = 0.01
	self.nb_iter = 8
	self.convergence_rate = 0.001

	#linking
	self.addLink('gradient_table','diffusion_data')
	self.addLink('mask','diffusion_data')
	self.addLink('response','diffusion_data')

	pass



def execution( self , context ):
	#loading light objects first
	gtab = load(self.gradient_table.fullPath())

	mask_vol = aims.read(self.mask.fullPath())
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






