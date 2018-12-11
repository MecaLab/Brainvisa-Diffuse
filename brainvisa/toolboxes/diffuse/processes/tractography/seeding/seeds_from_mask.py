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
from dipy.tracking.utils import seeds_from_mask
from brainvisa.registration import getTransformationManager
import numpy as np

name = 'Evenly distributed seeds from mask'
userLevel = 2

## Readout time (in sec)

signature = Signature(
	'mask', ReadDiskItem(
		'Diffusion MR Mask',
		'Aims readable volume formats'),
	'nb_seeds_x', Integer(),
	'nb_seeds_y', Integer(),
	'nb_seeds_z', Integer(),
	'seeds', WriteDiskItem(
		'Seeds',
		'Text File'
	),
)


def initialization(self):
	self.nb_seeds_x = self.nb_seeds_y = self.nb_seeds_z = 1
	self.addLink('seeds','mask')
	pass


def execution(self, context):

	mask_vol = aims.read(self.mask.fullPath())
	h = mask_vol.header()
	mask = np.asarray(mask_vol)[..., 0]
	mask = mask.astype(bool)
	voxel_size = np.array(h['voxel_size'])
	if len(voxel_size) == 4:
		voxel_size[-1] = 1
	elif len(voxel_size) == 3:
		voxel_size = np.concatenate((voxel_size,np.ones(1)))
	scaling = np.diag(voxel_size)

	density = [self.nb_seeds_x, self.nb_seeds_y, self.nb_seeds_z ]
	seeds = seeds_from_mask(mask, density=density,affine=scaling)
	np.savetxt(self.seeds.fullPath(), seeds)

	transformManager = getTransformationManager()
	transformManager.copyReferential(self.mask, self.seeds)
