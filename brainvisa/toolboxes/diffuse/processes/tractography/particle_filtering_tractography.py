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
from brainvisa.registration import getTransformationManager
from dipy.io.streamline import save_trk
from dipy.data import get_sphere
from dipy.tracking.local import ParticleFilteringTracking, ActTissueClassifier, CmcTissueClassifier
from dipy.direction.probabilistic_direction_getter import DeterministicMaximumDirectionGetter, ProbabilisticDirectionGetter
from brainvisa.diffuse.building_spheres import read_sphere
from copy import copy



userLevel = 0
name = 'Particle Filtering Tracking'


signature = Signature(
    'sh_coefficients', ReadDiskItem(
        'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'type',Choice('DETERMINISTIC','PROBABILISTIC'),

    'constraint', Choice(('Anatomical Constraint','ACT'),('Continuous Map Criterion','CMC')),
    'wm_pve',ReadDiskItem(
        'WM PVE Diffusion MR',
        'gz compressed NIFTI-1 image'
    ),
    'gm_pve', ReadDiskItem(
        'GM PVE Diffusion MR',
        'gz compressed NIFTI-1 image'
    ),
    'csf_pve', ReadDiskItem(
        'CSF PVE Diffusion MR',
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
    'fixed_step', Boolean(),
    'nb_iter_max', Integer(),
    'back_tracking_dist', Float(),
    'front_tracking_dist', Float(),
    'nb_particles',Integer(),
    'max_trial',Integer(),
    'return_all', Boolean(),
    'nb_samples', Integer(),
    'streamlines', WriteDiskItem(
        'Streamlines',
        'Trackvis tracts'
    ),
)

DirectionGetter = {'DETERMINISTIC': DeterministicMaximumDirectionGetter, 'PROBABILISTIC': ProbabilisticDirectionGetter}
Classifiers = {'CMC': CmcTissueClassifier, 'ACT': ActTissueClassifier}

def switching_type(self,dumb):
    signature = copy(self.signature)
    if self.type == 'DETERMINISTIC':
        self.nb_sample = 1
        self.nb_iter_max = 500
        self.setHidden('nb_samples')
    elif self.type == 'PROBABILISTIC':
        self.nb_samples = 5000
        self.nb_iter_max = 1000
        self.setEnable('nb_samples')
    self.changeSignature(signature)


def initialization(self):

    #Defualt values
    self.type = 'DETERMINISTIC'
    self.max_angle = 30
    self.relative_peak_threshold = 0.1
    self.min_separation_angle = 5
    self.step_size = 0.1
    self.fixed_step = True
    self.nb_iter_max = 300
    self.return_all = False
    self.nb_samples = 1
    self.crossing_max = None
    self.back_tracking_distance = 2
    self.front_tracking_dist = 1
    self.max_trial = 10
    self.nb_particles = 15
    self.setOptional('crossing_max','sphere')
    #to be coherent with local tractography
    self.constraint = 'ACT'
    self.addLink('mask','sh_coefficients')
    self.addLink('scalar_volume','sh_coefficients')
    self.addLink('seeds','sh_coefficients')
    self.addLink('csf_pve', 'sh_coefficients')
    self.addLink('gm_pve', 'sh_coefficients')
    self.addLink('wm_pve', 'sh_coefficients')
    self.addLink(None,'type',self.switching_type)
    self.addLink('streamlines','sh_coefficients')
    pass



def execution(self,context):

    sh_coeff_vol = aims.read(self.sh_coefficients.fullPath())
    header = sh_coeff_vol.header()

    #transformation from Aims LPI mm space to RAS mm (reference space)

    aims_mm_to_ras_mm = np.array(header['transformations'][0]).reshape((4,4))
    voxel_size = np.array(header['voxel_size'])
    if len(voxel_size) == 4:
        voxel_size = voxel_size[:-1]
    scaling = np.concatenate((voxel_size, np.ones(1)))
    context.write(voxel_size.shape)
    scaling_mat = np.diag(scaling)
    context.write(scaling_mat.shape, aims_mm_to_ras_mm.shape )
    aims_voxel_to_ras_mm = np.dot(scaling_mat,aims_mm_to_ras_mm)


    affine_tracking = np.eye(4)

    sh = np.array(sh_coeff_vol,copy=True)
    sh = sh.astype(np.float64)
    vol_shape = sh.shape[:-1]
    if self.sphere is not None:
        sphere = read_sphere(self.sphere.fullPath())
    else:
        context.write('No Projection Sphere provided. Default dipy sphere symmetric 362 is used' )
        sphere = get_sphere()


    dg = DirectionGetter[self.type].from_shcoeff(sh,self.max_angle,sphere,basis_type=None,relative_peak_threshold=self.relative_peak_threshold,min_separation_angle=self.min_separation_angle)

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


    csf_vol = aims.read(self.csf_pve.fullPath())
    grey_vol = aims.read(self.gm_pve.fullPath())
    white_vol = aims.read(self.wm_pve.fullPath())

    csf = np.array(csf_vol)
    csf = csf[..., 0]
    gm = np.array(grey_vol)
    gm = gm[..., 0]
    wm = np.array(white_vol)
    wm = wm[..., 0]

    #rethreshold volumes due to interpolation (eg values >1)
    total = (csf + gm + wm).copy()
    csf[total<=0] = 0
    gm[total<=0] = 0
    wm[total<=0] = 0
    csf[total!=0]= (csf[total !=0 ])/(total[total!=0])
    wm[total != 0] = (wm[total != 0])/(total[total != 0])
    gm[total != 0] = gm[total != 0] / (total[total != 0])

    classif = Classifiers[self.constraint]
    classifier = classif.from_pve(wm_map=wm, gm_map=gm, csf_map=csf)


    #Tracking is made in the LPI voxel space in order no to imposes affine to data. The seeds are supposed to also be in LPI voxel space
    streamlines_generator = ParticleFilteringTracking(dg, classifier,seeds,affine_tracking,step_size=self.step_size,max_cross=self.crossing_max, maxlen=self.nb_iter_max,pft_back_tracking_dist=self.back_tracking_dist, pft_front_tracking_dist=self.front_tracking_dist,pft_max_trial=self.max_trial,particle_count=self.nb_particles,return_all=self.return_all)
    #Store Fibers directly in  LPI orientation with appropriate transformation
    save_trk(self.streamlines.fullPath(),streamlines_generator,affine=aims_voxel_to_ras_mm,vox_size=voxel_size,shape=vol_shape)

    transformManager = getTransformationManager()
    transformManager.copyReferential(self.sh_coefficients, self.streamlines)










