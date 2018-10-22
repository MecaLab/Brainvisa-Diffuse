from soma import aims
import numpy as np
from copy import copy
from dipy.core.gradients import gradient_table_from_bvals_bvecs

################################################################
#I/O handling with AIMS library: simple wrappers
################################################################


def array_to_vol(array, header=None, dtype=np.float32):
	"""Convert an numpy array into an aims Volume properly:
	header is updated taking into account array properties
	"""
	new_arr = array.astype(dtype)
	arr = np.array(new_arr, order='F')
	vol = aims.Volume(arr)
	if header is not None:
		shape = list(new_arr.shape)
		index_max = len(shape)
		header['sizeX'] = shape[0]
		header['sizeY'] = shape[1]
		header['sizeZ'] = shape[2]
		if index_max == 3 :
			header['sizeT']= 1
		else:
			header['sizeT'] = shape[3]

		vol.header().update(header)
	return vol


def vol_to_array(aimsvolume):
	array = np.asarray(aimsvolume)
	if array.shape[-1]==1:
		array = array[..., 0]
	return array

def array_to_mask(array):
	mask = array.astype(bool)
	return mask



def extract_odf(objectfit, mask, sphere):

	shape = mask.shape + (len(sphere.vertices),)
	final_odf = np.zeros(shape)
	extraction = objectfit[mask]
	odf = extraction.odf(sphere)
	final_odf[mask] = odf
	return final_odf


#Handling shells


def shells(gtab):
	return np.unique(gtab.bvals)

def max_shell(gtab):
	s = shells(gtab)
	m = np.max(s)
	return m

def is_multi_shell(gtab):
	s = shells(gtab)
	if len(s[s!=0]) > 1:
		return True
	else:
		return False

def select_outer_shell(gtab):
	bvals = gtab.bvals
	bvecs = gtab.bvecs
	max_bval = np.max(shells(gtab))
	bvals [bvals != max_bval] = 0
	new_gtab = gradient_table_from_bvals_bvecs(bvals,bvecs)
	return new_gtab


def vertices_to_voxel(vertices, voxel_size):
	'''Transform vertices coordinates obtained from mesh into voxel coordinates
	Remark: we assume that vertices are already in the work space (LPI) for aims
	vertices is supposed to be an (N,3) array and voxel size an (3,) array '''
	voxels = vertices /voxel_size[np.newaxis,:]
	voxels = np.round(voxels,0)
	voxels = voxels.astype(int)
	return voxels

def vox_to_mask(voxels,shape):
	mask = np.zeros(shape,dtype=bool)
	vx, vy, vz = voxels[:, 0], voxels[:, 1], voxels[:, 2]
	mask[(vx,vy,vz)] = True
	return mask


def voxels_to_mask(voxels,shape,size):
	"""Given voxels coordinates of a volume of shape shapdistance """

	mask = np.zeros(shape,dtype=bool)
	s_x , s_y, s_z = size
	v_x,v_y,v_z = voxels[:,0],voxels[:,1],voxels[:,2]


	for i, idx in enumerate(v_x):
		idy = v_y[i]
		idk = v_z[i]
		#fixme: horrible but since numpy 1.6 on cluster does not have broadcasting and meshgrid functions
		xmin =  int(max(idx - s_x,0))
		xmax =  int(min(idx + s_x +1,shape[0]))
		ymin = int(max(idy - s_y, 0))
		ymax = int(min(idy + s_y + 1, shape[1]))
		zmin = int(max(idk - s_z, 0))
		zmax = int(min(idk + s_z + 1, shape[2]))
		#mask[v_x_min[i]:v_x_max[i],v_y_min[j]:v_y_max[j],v_z_min[k]:v_z_max[k]] = True
		mask[xmin:xmax,ymin:ymax,zmin:zmax] = True
	return mask















