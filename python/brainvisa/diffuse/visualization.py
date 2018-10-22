# coding: utf8

'''
Visualization module: this module regroups all function related to display , meshes and textures
It is essentially about computation of spherical function, display of dots at given locations
and texturing
'''

import numpy as np
from soma import aims


def quickview_spherical_functions(centers, unit_sphere, spherical_function):
	'''
	Compute vertices and faces for a mesh by modulating a sphere by spherical function
	centers correspond to the central location where the mesh are located.
	Remark: it is fast because of broadcasting but for big entry arrays it can requires a lot of memory
	:param centers: (N1, 3) nd array
	:param sphere: a Sphere Object (dipy) with vertices and faces.
	:param spherical_function: (N1,N_vertices) ndarray
	:return:
	new_vertices
	'''
	vertices = unit_sphere.vertices
	#multiply unit sphere vertices coordinates by spherical function amplitude using broadcasting
	spherical_points = spherical_function[:, :, np.newaxis] * vertices[np.newaxis, :, :]
	#translate the obtained spherical blobs to the proper location using broadcasting
	new_vertices = centers[:, np.newaxis,:] + spherical_points

	faces = unit_sphere.faces
	#reindex the faces so that the display will be coherent
	new_faces = len(vertices)*np.arange(len(centers))[:,np.newaxis, np.newaxis] + faces[np.newaxis,:,:]
	#flatten both vertices and faces to pass them to a mesh
	new_vertices = new_vertices.reshape((-1,3))
	new_faces = new_faces.reshape((-1,3))

	return new_vertices, new_faces



def quick_replicate_meshes(positions, vertices,faces):
	"""
	Replicate a mesh or sphere object by broadcasting its vertices and concatenating faces
	Useful to display small spheres at given location as an example. Remark if a time mesh is used no need to broadcast
	faces. Remark : it is fast because of broadcasting but can requires a lot of memory especially if the positions ndarray
	has huge lenght. An alternative is to concatenate meshes using pyAims corresponding function
	:param positions: (N,3) ndarray
	:param vertices: (N1, 3) ndarray
	:param faces:
	:return:
	"""

	new_vertices = positions[:,np.newaxis,:] + vertices[np.newaxis,:,:]
	new_faces  = len(vertices)*np.arange(len(positions))[:,np.newaxis, np.newaxis] + faces[np.newaxis,:,:]
	new_vertices = new_vertices.reshape((-1, 3))
	new_faces = new_faces.reshape((-1, 3))

	return new_vertices, new_faces


def vertices_and_faces_to_mesh(vertices, faces):
	'''
	Create an aims 3D mesh using precomputed vertices and faces. Vertices and faces are assumed to be compatible
	:param vertices: ndarray
	:param faces: ndarray
	:return: aims mesh
	'''
	#determine the mesh type based on polygon type (does not work for quads polygon !)
	poly_type = faces.shape[-1]
	mesh = aims.TimeSurface(dim=poly_type)
	v = mesh.vertex()
	p = mesh.polygon()

	v.assign([aims.Point3df(x) for x in vertices])
	
	p.assign([aims.AimsVector(x, dtype='U32', dim=poly_type) for x in faces])
	#recompute normals, not mandatory but to have coherent mesh
	mesh.updateNormals()
	return mesh

def array_to_texture(array):
	'''
    Build a TimeTexture from numpy array
	:param array: Text dim, temporal dim
	:return: aims TimeTexture object
	'''
	#numpy new behavior is to have float64 by default
	# cast it to float32 to use the TimeTexture method
	if array.dtype == 'float64':
		array = array.astype(np.float32)
	texture = aims.TimeTexture(array)
	return texture

def texture_to_label_texture(texture):
	"""Convert a texture into a label (S16) texture
	:param texture: AimsTimeTexture
	:return label_texture: AimsTimeTexture with int16 type (label)
	"""
	t = np.asarray(texture)
	#transpose due to weird handling of numpy array in TimeTexture class
	l = np.transpose(t)
	l = l.astype(np.int16)
	label_texture = aims.TimeTexture(l)
	return label_texture




























