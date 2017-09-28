# # -*- coding: utf-8 -*-
# #  This software and supporting documentation are distributed by
# #      Institut Federatif de Recherche 49
# #      CEA/NeuroSpin, Batiment 145,
# #      91191 Gif-sur-Yvette cedex
# #      France
# #
# # This software is governed by the CeCILL license version 2 under
# # French law and abiding by the rules of distribution of free software.
# # You can  use, modify and/or redistribute the software under the
# # terms of the CeCILL license version 2 as circulated by CEA, CNRS
# # and INRIA at the following URL "http://www.cecill.info".
# #
# # As a counterpart to the access to the source code and  rights to copy,
# # modify and redistribute granted by the license, users are provided only
# # with a limited warranty  and the software's author,  the holder of the
# # economic rights,  and the successive licensors  have only  limited
# # liability.
# #
# # In this respect, the user's attention is drawn to the risks associated
# # with loading,  using,  modifying and/or developing or reproducing the
# # software by the user in light of its specific status of free software,
# # that may mean  that it is complicated to manipulate,  and  that  also
# # therefore means  that it is reserved for developers  and  experienced
# # professionals having in-depth computer knowledge. Users are therefore
# # encouraged to load and test the software's suitability as regards their
# # requirements in conditions enabling the security of their systems and/or
# # data to be ensured and,  more generally, to use and operate it in the
# # same conditions as regards security.
# #
# # The fact that you are presently reading this means that you have had
# # knowledge of the CeCILL license version 2 and that you accept its terms.
#
#
#
# from brainvisa.processes import *
# from brainvisa.diffuse.tools import extract_odf, vol_to_array, array_to_mask, array_to_vol
# from soma import aims
# import numpy as np
# from joblib import load
# from dipy.data import get_sphere, Sphere
# from dipy.reconst.dti import TensorFit
#
# # userLevel = 2
# name = 'Diffusion Tensor Imaging (DTI) d-ODF'
# # category = 'model'
#
# signature = Signature(
# 	'tensor_coefficients', ReadDiskItem(
# 		'Diffusion Tensor Coefficients',
#         'gz compressed NIFTI-1 image'
# 	),
# 	'tensor_model', ReadDiskItem(
# 		'Diffusion Tensor Model',
#         'Joblib Pickle file'
# 	),
#     'sample_sphere', Choice(
#         ('default',
#          'symmetric362'),
#         ('symmetric724',
#          'symmetric724'),
#         ('custom', 'custom_sphere')
#     ),
#     'sphere', ReadDiskItem(
#         'Sphere',
#         'BrainVISA mesh formats'
#     ),
# 	'mask', ReadDiskItem(
# 		'Diffusion MR Mask',
#         'Aims readable volume formats'
#     ),
# 	'd-odf', WriteDiskItem(
# 		'Orientation Distribution Function',
# 		'gz compressed NIFTI-1 image'
# 	),
# )
#
#
#
#
#
# def initialization(self):
# 	self.addLink('tensor_model','tensor_coefficients')
# 	self.addLink('mask', 'tensor_coefficients')
# 	self.addLink('d-odf','tensor_coefficients')
# 	self.sample_sphere = 'default'
# 	self.setHidden('tensor_model','sphere')
# 	self.setOptional('sphere')
#
#
# def execution(self, context):
#
# 	tensor_coeff = aims.read(self.tensor_coefficients.fullPath())
# 	hdr = tensor_coeff.header()
# 	tensor = np.asarray(tensor_coeff)
# 	tensor_model = load(self.tensor_model.fullPath())
# 	tensorfit = TensorFit(tensor_model, tensor)
#
# 	mask_vol = aims.read(self.mask.fullPath())
# 	mask = vol_to_array(mask_vol)
# 	mask = array_to_mask(mask)
#
#
# 	if self.sample_sphere != 'custom':
# 		sphere = get_sphere()
# 		context.write(type(sphere))
# 	else :
# 		sphere_mesh = aims.read(self.sphere.fullPath())
# 		vertices = np.array(sphere_mesh.vertex())
# 		sphere = Sphere(xyz=vertices)
#
# 	odf = extract_odf(tensorfit, mask, sphere)
# 	odf_vol = array_to_vol(odf, header=hdr)
# 	aims.write(odf_vol,self.f_odf.fullPath())
#
# 	pass
#
#
#
#
#
#
#
#
#
# #
# #
