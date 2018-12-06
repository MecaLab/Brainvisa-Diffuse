#
# from brainvisa.processes import *
# from brainvisa.diffuse.tools import vol_to_array, array_to_vol, array_to_mask,max_shell,is_multi_shell,shells,select_outer_shell
# from soma import aims
# import numpy as np
# from joblib import load, dump
# from dipy.reconst.dti import TensorFit
# from dipy.reconst.csdeconv import response_from_mask
#
#
# userLevel = 2
# #roles = ('',)
# name = 'Fiber Impulsionnal Response DTI Estimation'
# category = 'Local_modeling'
#
# signature = Signature(
#
#     'tensor_coefficients', ReadDiskItem(
#         'Diffusion Tensor Coefficients',
#         'gz compressed NIFTI-1 image'
#     ),
#     'tensor_model', ReadDiskItem(
#         'Diffusion Tensor Model',
#         'Joblib Pickle file'
#     ),
#     'diffusion_data', ReadDiskItem(
#         'Corrected DW Diffusion MR',
#         'Aims readable volume formats'
#     ),
#     'gradient_table', ReadDiskItem(
#         'Gradient Table',
#         'Joblib Pickle file'
#     ),
#     'mask', ReadDiskItem(
#         'Diffusion MR Mask',
#         'Aims readable volume formats'
#     ),
#     'response', WriteDiskItem(
#         'Single Fiber Response',
#         'Joblib Pickle File'
#     ),
#
# )
#
#
#
#
# def initialization ( self ):
#
#
#
#     #linking
#     self.addLink('gradient_table','diffusion_data')
#     self.addLink('mask','diffusion_data')
#     self.addLink('response','diffusion_data')
#     self.setOptional('mask')
#
#     pass
#
#
#
# def execution( self , context ):
#
#     #if an existing tensor has already been fitted uses it
#     if self.tensor_coefficients is not None:
#         tensor_coeff_vol = aims.read(self.tensor_coefficients.fullPath())
#     	tensor_coeff = np.asarray(tensor_coeff_vol)
#    		 hdr = tensor_coeff_vol.header()
#     	tensor_model = load(self.tensor_model.fullPath())
#     	tenfit = TensorFit(tensor_model, tensor_coeff)
# 	    if self.mask is not None:
#
#
#     else
#
#     gtab = load(self.gradient_table.fullPath())
#
#     if is_multi_shell(gtab):
#         context.warning("The DWI scheme for this data is multishell: bvalues", shells(gtab),
#                     ". CSD implementation used in Diffuse currently only handle single shell DWI scheme. By default the higher shell bval",
#                         max_shell(gtab), " is selected")
#         context.warning("Even if only the outer shell is use for deconvolution, the following estimation method will use the full DWI scheme for response estimation. It might be inaccurate  if the deconvolved shell bvalue is too high (b5000)")
#
#     vol = aims.read(self.diffusion_data.fullPath())
#     data = np.asarray(vol)
#
#     if self.mask is not None:
#         mask_vol = aims.read(self.mask.fullPath())
#         mask = vol_to_array(mask_vol)
#         mask = array_to_mask(mask)
#     else:
#         context.warning("No mask provided ! ")
#         mask = np.ones(data.shape[:-1])
#
#     response,ratio = response_from_mask(gtab,data,mask)
#
#     dump(response, self.response.fullPath())
#
#
#
#
#
#
