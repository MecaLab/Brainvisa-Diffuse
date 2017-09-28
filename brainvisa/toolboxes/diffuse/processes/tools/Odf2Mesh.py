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
from soma import aims
from brainvisa.diffuse.visualization import quickview_spherical_functions,vertices_and_faces_to_mesh, array_to_texture
from brainvisa.diffuse.building_spheres import read_sphere



signature = Signature(
	'spherical_function', ReadDiskItem('Orientation Distribution Function', 'gz compressed NIFTI-1 image'),
	'sphere', ReadDiskItem('Sphere Template','GIFTI File'),
	'scaling_factor', Float(),
	'mesh', WriteDiskItem('Spherical Function Mesh','GIFTI file'),
	'texture', WriteDiskItem('Spherical Function Texture','GIFTI file')

)


def initialization(self):
	self.addLink('mesh','spherical_function')
	self.addLink('texture','mesh')
	self.setOptional('texture')
	self.scaling_factor = 1.0


def execution(self,context):

	spherical_function = aims.read(self.spherical_function.fullPath())
	#only valid if volume is isotropic
	vox_size = np.array(spherical_function.header()['voxel_size'])[0]
	sf = np.asarray(spherical_function)
	sphere = read_sphere(self.sphere.fullPath())

	assert len(sphere.vertices) == sf.shape[-1]
	#removing all non physical values
	sf[sf<0] = 0
	context.write(sf.shape)
	index = np.where(np.all(sf == 0, axis=-1) == False)
	context.write(len(index[0]))
	sf_function = sf[index].copy()
	context.write(sf_function.shape)

	del sf
	################################################""###""""""
	#Normalisation to have distributions (the 2 is to reach size 1 (voxel)
	sf_vizu = sf_function.copy()
	sf_vizu = sf_vizu / (np.sum(sf_function,axis=1)[..., np.newaxis])
	context.write(sf_function.shape)
	sf_vizu = sf_vizu/(2*sf_vizu.max())

	sf_vizu = sf_vizu * vox_size

	sf_vizu = sf_vizu*self.scaling_factor


	centers = np.zeros((len(index[0]), 3))
	centers[:,0] = index[0]
	centers[:,1] = index[1]
	centers[:,2] = index[2]
	centers = centers * vox_size

	vertices,faces = quickview_spherical_functions(centers,sphere,sf_vizu)
	mesh = vertices_and_faces_to_mesh(vertices,faces)

	#creation of the texture

	texture = aims.TimeTexture('FLOAT')
	visu = sf_function.flatten()
	t= texture[0]
	t.reserve(len(visu))
	for i in range(len(visu)):
		t[i]= visu[i]

	#saving mesh and texture

	aims.write(mesh,self.mesh.fullPath())
	aims.write(texture, self.texture.fullPath())



