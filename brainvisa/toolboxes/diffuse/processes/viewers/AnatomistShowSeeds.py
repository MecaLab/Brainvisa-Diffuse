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
from brainvisa import anatomist
from soma import aims
import numpy as np
from scipy.spatial.distance import pdist
from brainvisa.registration import getTransformationManager
from brainvisa.diffuse.visualization import quick_replicate_meshes,vertices_and_faces_to_mesh,array_to_texture


userLevel = 0
name = 'Anatomist Show Seeds as spheres'
roles = ('viewer', )

signature = Signature(
    'seeds', ReadDiskItem(
        'Seeds',
        'Text File'
    ),
    'n_sampling',Integer(),
    'n_display', Integer(),
)


def validation():
  anatomist.validation()


def initialization(self):

    self.n_sampling = 500
    self.n_display = 10000
    pass


def execution(self, context):
    n_faces = 21
    transformManager = getTransformationManager()
    seeds_referential = transformManager.referential(self.seeds)

    seeds_centers = np.loadtxt(self.seeds.fullPath())
    n_sample = min(len(seeds_centers), self.n_sampling)
    if len(seeds_centers) > self.n_display:
        context.warning(
            "You try to display more than ", str(self.n_display), " seeds. It may causes Memory Error. The first ", str(self.display)," seeds ONLY are displayed in order to prevent crashes")
    radius = np.min(pdist(seeds_centers[:n_sample])) / 2.0
    sphere = aims.SurfaceGenerator.icosphere((0, 0, 0), radius, n_faces)
    vertices = np.array(sphere.vertex())
    triangles = np.array(sphere.polygon())
    seeds_centers = seeds_centers[:min(self.n_display, len(seeds_centers))]
    new_vertices, new_triangles = quick_replicate_meshes(seeds_centers, vertices, triangles)
    mesh = vertices_and_faces_to_mesh(new_vertices, new_triangles)

    a = anatomist.Anatomist()
    w3d = a.createWindow("3D")

    A_graph = a.toAObject(mesh)
    #yellow colors for the seeds (different form Red, Green , Blue so that they appears with orientation coded fibers
    material = a.Material(diffuse=[1, 1, 0, 1])
    A_graph.setMaterial(material)
    A_graph.assignReferential(seeds_referential)
    w3d.addObjects(A_graph)
    return [w3d, A_graph]