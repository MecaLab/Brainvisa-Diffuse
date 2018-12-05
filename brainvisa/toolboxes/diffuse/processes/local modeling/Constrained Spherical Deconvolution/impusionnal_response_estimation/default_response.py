
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
name = 'Fiber Impulsionnal Response: Default Prolate Response'
category = 'Local_modeling'

signature = Signature(
	'diffusion_data', ReadDiskItem(
		'Corrected DW Diffusion MR',
		'Aims readable volume formats'
	),
	'response', WriteDiskItem(
		'Single Fiber Response',
		'Joblib Pickle File'
	),
)



def initialization ( self ):
	self.addLink('response','diffusion_data')
	pass


def execution( self , context ):
	response = (np.array([0.0015, 0.0003, 0.0003]), 1)
	context.write("Use long prolate tensor as used in Catani to deconvolve the signal",response)
	dump(response, self.response.fullPath())






