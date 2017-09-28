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
import numpy as np
from dipy.tracking.local import LocalTracking,ActTissueClassifier,BinaryTissueClassifier,ThresholdTissueClassifier
from dipy.direction.probabilistic_direction_getter import DeterministicMaximumDirectionGetter, ProbabilisticDirectionGetter
from brainvisa.diffuse.building_spheres import read_sphere
from copy import copy
from dipy.io.trackvis import save_trk
from dipy.tracking.utils import move_streamlines
from dipy.core.sphere import Sphere
import nibabel as nib
from dipy.data import get_sphere
from soma import aims


userLevel = 2
name = 'Local Tracking'




signature = Signature(
	'sh_coefficients', ReadDiskItem(
		'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
	),
	'type',Choice('DETERMINISTIC','PROBABILISTIC'),

	'constraint', Choice('Binary','Threshold','Anatomical'),
	'mask', ReadDiskItem(
		'Diffusion MR Mask',
		'gz compressed NIFTI-1 image'
	),
	'scalar_volume', ReadDiskItem(
		'Fractionnal Anisotropy Volume',
		'gz compressed NIFTI-1 image'
	),
	'include_pve_map', ReadDiskItem(
		'Diffusion MR Mask',
		'gz compressed NIFTI-1 image'
	),
	'exclude_pve_map',ReadDiskItem(
		'Diffusion MR Mask',
		'gz compressed NIFTI-1 image'
	),
	'threshold',Float(),

	'sphere', ReadDiskItem(
		'Sphere Template',
		'GIFTI file'
	),
	'seeds', ReadDiskItem(
		'Seeds',
		'Text File'
	),
	'max_angle', Float(),
	'relative_peak_threshold', Float(),
	'min_separation_angle',Float(),
	'crossing_max', Integer(),
	'step_size', Float(),
	'fixed_step', Boolean(),
	'nb_iter_max', Integer(),
	'return_all',Boolean(),
	'nb_samples',Integer(),
	'streamlines',WriteDiskItem(
		'Raw Streamlines',
		'Numpy Array'
	),
	# 'visu_streamlines', WriteDiskItem(
	# 	'Bundles',
	# 	'Trackvis tracts'
	# ),
)

DirectionGetter = {'DETERMINISTIC':DeterministicMaximumDirectionGetter,'PROBABILISTIC': ProbabilisticDirectionGetter}

def switching_type(self,dumb):
	signature = copy(self.signature)
	if self.type == 'DETERMINISTIC':
		self.nb_sample = 1
		self.nb_iter_max = 500
		self.setHidden('nb_samples')
	elif self.type == 'PROBABILISTIC':
		self.nb_samples = 5
		self.nb_iter_max = 1000
		self.setEnable('nb_samples')
	self.changeSignature(signature)

def switching_classifier(self,dumb):
	signature = copy(self.signature)
	if self.constraint == 'Binary':
		self.setHidden('scalar_volume','include_pve_map','exclude_pve_map','threshold')
		self.setOptional('scalar_volume','include_pve_map','exclude_pve_map','threshold')
		self.setEnable('mask')
	elif self.constraint == 'Threshold':
		self.setHidden('mask', 'include_pve_map', 'exclude_pve_map')
		self.setEnable('scalar_volume','threshold')
	elif self.constraint == 'Anatomical':
		self.setHidden('scalar_volume', 'mask' , 'threshold')
		self.setEnable('include_pve_map','exclude_pve_map')
		self.setOptional('mask')
	self.changeSignature(signature)




def initialization(self):

	self.type='DETERMINISTIC'
	self.max_angle = 30
	self.relative_peak_threshold = 0.1
	self.min_separation_angle = 5
	self.step_size = 0.1
	self.fixed_step = True
	self.nb_iter_max = 300
	self.return_all = False
	self.nb_samples = 1
	self.crossing_max = None
	self.setOptional('crossing_max')

	self.addLink('mask','sh_coefficients')
	self.addLink('scalar_volume','sh_coefficients')
	self.addLink('seeds','sh_coefficients')
	self.addLink(None,'type',self.switching_type)
	self.addLink(None,'constraint',self.switching_classifier)
	self.addLink('streamlines','sh_coefficients')
	# self.addLink('visu_streamlines','working_streamlines')
	#self.setOptional('visu_streamlines')


	pass



def execution(self,context):

	sh_coeff_vol = aims.read(self.sh_coefficients.fullPath())
	header = sh_coeff_vol.header()
	storage_2_mem = np.array(aims.AffineTransformation3d(header['storage_to_memory']).inverse().toMatrix())
	storage_2_mem = 1.25*storage_2_mem
	storage_2_mem[3,3] = 1
	context.write(storage_2_mem)
	vox_size = header['voxel_size'][:-1]
	sh = np.array(sh_coeff_vol,copy=True)
	sh = sh.astype(np.float64)
	sphere = read_sphere(self.sphere.fullPath())
	#sphere = get_sphere()
	dg = DirectionGetter[self.type].from_shcoeff(sh,self.max_angle,sphere,basis_type=None,relative_peak_threshold=self.relative_peak_threshold,min_separation_angle=self.min_separation_angle)
	#tractography is done in voxel space it is more convenient
	affine = np.eye(4)
	#Handling seeds in both deterministic and probabilistic framework
	s = np.loadtxt(self.seeds.fullPath())
	s = s.astype(np.float32)
	i = np.arange(self.nb_samples)
	if self.nb_samples <=1 :
		seeds = s
	else:
		seeds = np.zeros((self.nb_samples,)+s.shape)
		seeds[i] = s
		seeds = seeds.reshape((-1,3))
	#building classifier

	if self.constraint == 'Binary':
		mask_vol = aims.read(self.mask.fullPath())
		mask = np.asarray(mask_vol)[...,0]
		mask = mask.astype(bool)
		classifier = BinaryTissueClassifier(mask)
	elif self.constraint == 'Threshold':
		scal_vol = aims.read(self.scalar_volume.fullPath())
		scal = np.asarray(scal_vol)[...,0]
		scal = scal.astype(np.float32)
		classifier = ThresholdTissueClassifier(scal, self.threshold)
	elif self.constraint == 'Anatomical':
		include_pve = np.asarray(aims.read(self.include_pve_map.fullPath()))[...,0]
		exclude_pve = np.asarray(aims.read(self.exclude_pve_map.fullPath()))[...,0]
		classifier = ActTissueClassifier(include_pve,exclude_pve)
	else:
		pass








	#Tracking is made in the LPI voxel space in order no to imposes affine to data. The seeds are supposed to also be in LPI voxel space
	streamlines = LocalTracking(dg, classifier,seeds,affine,step_size=self.step_size,max_cross=self.crossing_max,maxlen=self.nb_iter_max,fixedstep=np.float32(self.fixed_step),return_all=self.return_all)
	bubu = np.zeros((4,4))
	i = np.arange(3)
	bubu[i,i] = 1.25
	bubu[3,3] = 1
	points = move_streamlines(streamlines, bubu)
	save_trk(self.visu_streamlines.fullPath(),points,storage_2_mem,sh.shape[:-1])

	# post_tracking classification mask wm
	# wm_mask = np.asarray(aims.read(self.wm_mask.fullPath()))[..., 0]
	# wm_mask = wm_mask.astype(bool)


	# vox_to_trk = np.diag(vox_size + [1])
	# #transfo from
	# context.write(vox_to_trk)
	# #move streamlines to RAS voxel space
	# streamlines = move_streamlines(streamlines, storage_2_mem)
	# streamlines = list(streamlines)
	# st_to_save = np.array(streamlines, dtype=object)
	# np.save(self.working_streamlines.fullPath(), st_to_save)
	# del st_to_save
	# #move streamlines to trackvis space
	# streamlines = move_streamlines(streamlines ,vox_to_trk)
	# data = ((p, None, None) for p in streamlines)
	# #building header
	# hdr = nib.trackvis.empty_header()
	# hdr['dim'] = sh.shape[:-1]
	# hdr['voxel_order'] = " RAS '"
	# hdr['voxel_size'] = vox_size
	# context.write(vox_size)
	# nib.trackvis.write(self.visu_streamlines.fullPath(), data, hdr)







