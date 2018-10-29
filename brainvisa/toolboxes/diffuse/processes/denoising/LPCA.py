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
from brainvisa.registration import getTransformationManager
from dipy.denoise.localpca import localpca
from brainvisa.diffuse.tools import vol_to_array, array_to_vol
from soma import aims

#default values used in dipy v0.14
PATCH_RADIUS = 2
TAU_FACTOR = 2.3


name = 'LPCA'
userLevel = 0

signature = Signature(
    'dwi_data', ReadDiskItem('Raw Diffusion MR', 'Aims readable volume formats'),
    'sigma', ReadDiskItem('Noise Standard Deviation','Aims readable volume formats'),
    'brain_mask', ReadDiskItem('T1 MRI to DW Diffusion MR Brain', 'Aims readable volume formats'),
    'method', Choice('eig', 'svd'),
    'patch_radius', Integer(),
    'tau_factor', Float(),
    'denoised_dwi_data', WriteDiskItem('Denoised Diffusion MR', 'gz compressed NIFTI-1 image'),
)

def initialization(self):
    self.linkParameters('denoised_dwi_data', 'dwi_data')
    self.linkParameters('sigma','dwi_data')
    self.linkParameters('brain_mask', 'dwi_data')
    self.brain_mask = None
    self.patch_radius = PATCH_RADIUS
    self.tau_factor = TAU_FACTOR
    self.method = 'eig'
    self.setOptional('brain_mask')


def execution(self, context):

    data_vol = aims.read(self.dwi_data.fullPath())
    header = data_vol.header()
    data = vol_to_array(data_vol)
    sigma_vol = aims.read(self.sigma.fullPath())
    sigma = vol_to_array(sigma_vol)
    if self.brain_mask is not None:
        brain_mask_vol = aims.read(self.brain_mask.fullPath())
        brain_mask = vol_to_array(brain_mask_vol)
    else:
        brain_mask = None

    denoised_data = localpca(data,sigma,mask=brain_mask, pca_method=self.method, patch_radius=self.patch_radius, tau_factor=self.tau_factor)
    denoised_data_vol = array_to_vol(denoised_data,header=header)
    aims.write(denoised_data_vol, self.denoised_dwi_data.fullPath())




