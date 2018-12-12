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
from dipy.denoise.noise_estimate import piesno
from brainvisa.diffuse.tools import vol_to_array, array_to_vol
from soma import aims
import numpy as np

#default values used in dipy v0.14
ALPHA = 0.01
EPS = 1e-05
TRIALS = 100
ITERMAX = 100


name = 'Piesno'
userLevel = 0

signature = Signature(
    'dwi_data', ReadDiskItem('Raw Diffusion MR', 'Aims readable volume formats'),
    'coil_number', Integer(),
    'alpha', Float(),
    'trials', Integer(),
    'itermax', Integer(),
    'eps', Float(),
    'sigma', WriteDiskItem('Noise Standard Deviation', 'gz compressed NIFTI-1 image'),
)

def initialization(self):
    self.linkParameters('sigma','dwi_data')
    self.alpha = ALPHA
    self.eps = EPS
    self.trials = TRIALS
    self.itermax = ITERMAX


def execution(self, context):

    data_vol = aims.read(self.dwi_data.fullPath())
    header = data_vol.header()
    data = vol_to_array(data_vol)
    sigma = piesno(data, self.coil_number, alpha=self.alpha, l=self.trials, itermax=ITERMAX, eps=EPS, return_mask=False)
    sigma_arr = sigma*np.ones(data.shape[:-1], dtype=np.float32)
    sigma_vol = array_to_vol(sigma_arr, header=header)
    aims.write(sigma_vol, self.sigma.fullPath())

