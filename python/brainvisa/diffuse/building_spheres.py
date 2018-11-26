# coding: utf8
import numpy as np
from soma import aims
from dipy.core.sphere import Sphere, HemiSphere
from dipy.data import get_sphere
from dipy.core.sphere import disperse_charges
from nibabel.affines import apply_affine
from brainvisa.diffuse.meshes import vertices_and_faces_to_mesh


#####################################################################
# SPHERE CREATION
#####################################################################

def create_symmetric_repulsion_sphere(n_points, n_iter):
	"""
	Create a full Sphere object using electrostatic repulsion.
	params:
	npoints: number of points in the electrostatic repulsion
	n_iter: number of iterations to optimise energy
	return: Sphere object with 2*npoints vertices
	"""
	theta = np.pi * np.random.rand(n_points)
	phi = 2 * np.pi * np.random.rand(n_points)
	hsph_initial = HemiSphere(theta=theta, phi=phi)
	hsph_updated,energy = disperse_charges(hsph_initial,iters=n_iter)
	sph = Sphere(xyz=np.vstack((hsph_updated.vertices, -hsph_updated.vertices)))
	return sph


def create_repulsion_sphere(n_points, n_iter):
	""" Create a sphere using electrostatic repulsion.
	params:
	npoints: number of points in the electrostatic repulsion
        n_iter: number of iterations to optimise energy
	return: HemiSphere object with n points vertices
	"""
	theta = np.pi * np.random.rand(n_points)
	phi = 2 * np.pi * np.random.rand(n_points)
	hsph_initial = HemiSphere(theta=theta, phi=phi)
	hsph_updated, energy = disperse_charges(hsph_initial,iters=n_iter)
	sph = hsph_updated
	return sph
	

def create_icosphere(n_facets,center=(0,0,0), radius=1):
	""" Generate a sphere using subdivision of an icosahedron:
	This kind of sphere is better for visualisation because do not induce préferential directions (see UV sphere)
	 Although the number of vertices and faces can not be controlled properly
	params:
	n_facets: number of faces wanted --> actual number of faces is the closest one to the n_facets verifying iscosaedral property
	return: mesh
	"""
	sphere = aims.SurfaceGenerator.icosphere(center, radius, n_facets)
	return sphere

#######################################################################
# SPHERE CONVERSION
#######################################################################

def sphere_to_mesh(sphere):
	'''
	convert a dipy sphere object into an aims Mesh
	:param sphere: Sphere object
	:return: Aims Mesh object
	'''

	vertices = sphere.vertices
	faces = sphere.faces
	mesh = vertices_and_faces_to_mesh(vertices,faces)
	return mesh

def mesh_to_sphere(mesh):
	vertices = np.array(mesh.vertex()).astype(np.float64)
	faces = np.array(mesh.polygon()).astype(np.uint16)
	sphere = Sphere(xyz=vertices,faces=faces)
	#step not necessary but just to be sure
	edges = sphere.edges.astype(np.uint16)
	sphere = Sphere(xyz=vertices,faces=faces,edges=edges)
	return sphere

#######################################################################
#SPHERE IO: 
#######################################################################

def read_sphere(path):
	"""
    Load a sphere stored as an AimsTimeSurface and create a Dipy Sphere Object.
    If no path is provided used the Dipy default sphere symmetric362
    """
	if path is not None:
		sphere_mesh = aims.read(path)
		sphere = mesh_to_sphere(sphere_mesh)
	else:
		sphere = get_sphere()
	return sphere

#######################################################################
# FACES ORIENTATIONS
#######################################################################
def compute_face_normals(faces, vertices):
	""" Compute the normals of the FACES of the sphere
    Method exist in aims but compute normals in each vertex (more stable)"""
	i = faces[:,0]
	j = faces[:,1]
	k = faces[:,2]
	cp = np.cross((vertices[j] -vertices[i]),(vertices[k] -vertices[i]))
	norm = np.sqrt(np.sum(cp**2,axis=1))
		#normalization is not even necessary but perform it
	normals = cp/norm[:,np.newaxis]
	return normals

def check_face_orientation(faces, vertices):
	""" Check if the faces all have the same orientation:
	Compute the dot product between faces normals an one of the faces' vertex"""
	f_normals = compute_face_normals(faces, vertices)
	v = vertices[faces[:,0]]
	s_product = np.sum(f_normals*v,axis=1)
	orientation_check = s_product < 0
	return orientation_check

def correct_sphere(sphere):
	faces = sphere.faces.copy()
	vertices = sphere.vertices
	o = check_face_orientation(faces,vertices)
	faces[o,:] = faces[o,::-1]
	new_sphere = Sphere(xyz=vertices,faces=faces)
	return new_sphere

########################################################################
# SPHERE MODIFICATIONS
########################################################################

def reorient_sphere(sphere, affine):
	v = apply_affine(affine,sphere.vertices)
	s = Sphere(xyz=v,faces=sphere.faces)
	return s

def create_mrtrix_sphere(theta, phi):
	mr_sphere = np.zeros((len(phi),2))
	mr_sphere[:,0] = phi
	mr_sphere[:,1] = theta
	return mr_sphere

def dipy_2_mrtrix(sphere,affine):
	reo_sphere = reorient_sphere(sphere,affine)
	mr_sphere = create_mrtrix_sphere(reo_sphere.theta, reo_sphere.phi)
	return mr_sphere






