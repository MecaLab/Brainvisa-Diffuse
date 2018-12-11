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
from copy import copy
import numpy as np


name = 'Seeds from white mesh'
userLevel = 0

## RePlace equidistant seeds (points) of every voxels of a given mask. Number of seeds is controlled along each direction.adout time (in sec)

signature=Signature(
	'white_mesh', ReadDiskItem(
		'Registered White Mesh',
		'GIFTI file'
	),
	'roi_texture',ReadDiskItem(
		'ROI Texture',
		'GIFTI file'
	),
	'seeds',WriteDiskItem(
	    'Seeds',
		'Text File'
	),
)

def initialization(self):
	self.setHidden('reference_volume')
	self.addLink('roi_texture','white_mesh')
	self.addLink('reference_volume', 'white_mesh')
	self.addLink('seeds', 'white_mesh')
	self.setOptional('roi_texture')
	pass


def execution(self,context):

	mesh = aims.read(self.white_mesh.fullPath())
	vertices = np.array(mesh.vertex())
	#extract texture
	if self.roi_texture is None:
		v = vertices
	else:
		texture = aims.read(self.roi_texture.fullPath())
		tex = np.array(texture[0])
		v = vertices[tex!=0]
	#voxels are in LPI mm space: put them in LPI voxel space
	minf = self.reference_volume.minf()
	v_size = np.array(minf['voxel_size'][:-1])
	v = v / v_size[np.newaxis,:]

	np.savetxt(self.seeds.fullPath(), v)









