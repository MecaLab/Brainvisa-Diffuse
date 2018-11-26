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
from dipy.tracking.local import ParticleFilteringTracking, ActTissueClassifier, CmcTissueClassifier
from dipy.io.streamline import save_trk
from dipy.direction.probabilistic_direction_getter import ProbabilisticDirectionGetter
from brainvisa.diffuse.building_spheres import read_sphere
from copy import copy

userLevel = 3
name = 'Particle Filtering Tracking'

signature = Signature(
    'sh_coefficients', ReadDiskItem(
        'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'constraint', Choice('ACT','CMC'),
    'include_pve_map', ReadDiskItem(
        'Diffusion MR Mask',
        'gz compressed NIFTI-1 image'
    ),
    'exclude_pve_map', ReadDiskItem(
        'Diffusion MR Mask',
        'gz compressed NIFTI-1 image'
    ),
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
    'min_separation_angle', Float(),
    'crossing_max', Integer(),
    'step_size', Float(),
    'back_tracking_dist', Float(),
    'front_tracking_dist', Float(),
    'max_trial',Integer(),
    'nb_iter_max', Integer(),
    'nb_particles',Integer(),
    'return_all', Boolean(),
    'nb_samples', Integer(),
    'streamlines', WriteDiskItem(
        'Streamlines',
        'Trackvis format'
    ),
)

DirectionGetter = {'PROBABILISTIC': ProbabilisticDirectionGetter}




def initialization(self):

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

    self.addLink('mask', 'sh_coefficients')
    self.addLink('scalar_volume', 'sh_coefficients')
    self.addLink('seeds', 'sh_coefficients')
    self.addLink(None, 'type', self.switching_type)
    self.addLink(None, 'constraint', self.switching_classifier)
    self.addLink('streamlines', 'sh_coefficients')
    pass


def execution(self, context):
    sh_coeff_vol = aims.read(self.sh_coefficients.fullPath())
    header = sh_coeff_vol.header()

    #getting voxel size
    voxel_size = np.array(header['voxel_size'])
    #remove the voxel size of diffusion voxel
    if len(voxel_size) == 4:
        vox_size = voxel_size[:-1]
    aims_mm_to_ras_mm = np.array(header['transformations'][0])
    scaling = np.concatenate((voxel_size, np.ones(1)))
    scaling_mat = np.diag(scaling)
    aims_voxel_to_ras_mm = np.dot((scaling_mat, aims_mm_to_ras_mm))
    sh = np.array(sh_coeff_vol, copy=True)
    sh = sh.astype(np.float64)
    shape = sh.shape[:-1]

    sphere = read_sphere(self.sphere.fullPath())
    # sphere = get_sphere()
    dg = DirectionGetter[self.type].from_shcoeff(sh, self.max_angle, sphere, basis_type=None,
                                                 relative_peak_threshold=self.relative_peak_threshold,
                                                 min_separation_angle=self.min_separation_angle)
    # tractography is done in voxel space it is more convenient
    affine = np.eye(4)
    # Handling seeds in both deterministic and probabilistic framework
    s = np.loadtxt(self.seeds.fullPath())
    s = s.astype(np.float32)
    i = np.arange(self.nb_samples)
    if self.nb_samples <= 1:
        seeds = s
    else:
        seeds = np.zeros((self.nb_samples,) + s.shape)
        seeds[i] = s
        seeds = seeds.reshape((-1, 3))
    # building classifier
    include_pve = np.asarray(aims.read(self.include_pve_map.fullPath()))[..., 0]
    exclude_pve = np.asarray(aims.read(self.exclude_pve_map.fullPath()))[..., 0]

    if self.constraint == 'CMC':
        classifier = CmcTissueClassifier(include_pve, exclude_pve)

    else:
        classifier = ActTissueClassifier(include_pve, exclude_pve)


    #Tracking is made in the LPI voxel space in order no to imposes affine to data. The seeds are supposed to also be in LPI voxel space
    streamlines_generator = ParticleFilteringTracking(dg, classifier, seeds, affine, step_size=self.step_size,
                                      max_cross=self.crossing_max, maxlen=self.nb_iter_max,pft_back_tracking_dist=self.back_tracking_dist,pft_front_tracking_dist=self.front_tracking_dist,pft_max_trial=self.max_trial,particle_count=self.nb_particles, return_all=self.return_all)

    save_trk(self.streamlines.fullPath(), streamlines_generator, affine=aims_voxel_to_ras_mm, vox_size=voxel_size, shape=shape)













