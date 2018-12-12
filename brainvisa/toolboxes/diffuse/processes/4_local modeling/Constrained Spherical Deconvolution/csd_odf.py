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
from joblib import load
from brainvisa.diffuse.tools import array_to_vol, array_to_mask, vol_to_array, extract_odf
from brainvisa.diffuse.building_spheres import read_sphere
from dipy.reconst.csdeconv import SphHarmFit

# userLevel = 0
name = 'Constrained Spherical Deconvolution (CSD) Fiber-ODF'
# category = 'model'

signature = Signature(
	'fibre_odf_sh_coeff', ReadDiskItem(
		'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
	),
	'csd_model', ReadDiskItem(
		'Constrained Spherical Deconvolution Model',
        'Joblib Pickle file'
	),
    'sphere', ReadDiskItem(
        'Sphere Template',
        'GIFTI file'
    ),
	'mask', ReadDiskItem(
		'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
	'fibre_odf', WriteDiskItem(
		'Orientation Distribution Function',
		'gz compressed NIFTI-1 image'
	),
)





def initialization(self):
	self.addLink('csd_model','fibre_odf_sh_coeff')
	self.addLink('mask', 'fibre_odf_sh_coeff')
	self.addLink('fibre_odf','fibre_odf_sh_coeff')
	self.setOptional('sphere')
	self.setHidden('csd_model')



def execution(self, context):
	#reading object from the lightest to the biggest in memory
	model = load(self.csd_model.fullPath())
	sphere = read_sphere(self.sphere.fullPath())
	mask_vol = aims.read(self.mask.fullPath())
	mask = vol_to_array(mask_vol)
	mask = array_to_mask(mask)

	sh_coeff_vol = aims.read(self.fibre_odf_sh_coeff.fullPath())
	hdr = sh_coeff_vol.header()
	sh_coeff = np.asarray(sh_coeff_vol)
	context.write("Data were successfully loaded.")
	spharmfit = SphHarmFit(model,sh_coeff, mask)

	odf = extract_odf(spharmfit, mask, sphere)
	#odf = spharmfit.odf(sphere)
	#do not use the classical dipy function because it compute odf for the whole volume by default and take far too much
	#memory.
	odf_vol = array_to_vol(odf, header=hdr)
	aims.write(odf_vol,self.fibre_odf.fullPath())

	pass








