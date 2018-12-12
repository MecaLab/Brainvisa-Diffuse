
from brainvisa.processes import *
import numpy as np
from joblib import load, dump



userLevel = 0
#roles = ('',)
name = 'Default Prolate Response'
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
	context.write("Use sharp prolate tensor as in Catani's publications [eg, ] to deconvolve the signal",response)
	dump(response, self.response.fullPath())






