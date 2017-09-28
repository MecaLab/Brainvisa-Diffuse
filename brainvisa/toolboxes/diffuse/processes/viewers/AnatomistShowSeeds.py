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
from brainvisa.diffuse.visualization import quick_replicate_meshes,vertices_and_faces_to_mesh,array_to_texture


userLevel = 0
name = 'Anatomist Show Seeds as spheres'
roles = ('viewer', )

signature = Signature(
    'seeds_coordinates', ReadDiskItem(
        'Seeds',
        'Text File'
    ),
    'reference_volume',ReadDiskItem(
        'Corrected DW Diffusion MR',
        'Aims readable volume formats'
    ),
)


def validation():
  anatomist.validation()


def initialization(self):
    self.addLink('reference_volume','seeds_coordinates')
    self.setHidden('reference_volume')
    pass


def execution(self, context):

    seeds_centers = np.loadtxt(self.seeds_coordinates.fullPath())

    #getting_voxel_size from metada of reference volume (rem: is it possible to create one referential with voxel size in it?)
    #remove the 1 size of 4D volume on loading
    voxel_size = np.array(self.reference_volume.minf()['voxel_size'])[:-1]
    context.write(seeds_centers.shape, voxel_size.shape)
    if voxel_size.shape[0]!= seeds_centers.shape[-1]:
        context.write('No compatible dimensions, aborting display')
    else:
        #putting seeds back in mm for visualization
        seeds_centers = seeds_centers*voxel_size[np.newaxis,:]

        #compute the min difference between two centers (can be long if too many seeds)
        n_sample = min(len(seeds_centers),500)
        if len(seeds_centers)>10000:
            context.warning("You try to display more than 10000 seeds. It can causes Memory Error. The 5000 first seeds ONLY are displayed in order to prevent crashes")
        radius = np.min(pdist(seeds_centers[:n_sample]))/2.0

        nfaces = 21
        sphere = aims.SurfaceGenerator.icosphere((0, 0, 0), radius, nfaces)
        vertices = np.array(sphere.vertex())
        triangles = np.array(sphere.polygon())

        seeds_centers = seeds_centers[:min(10000,len(seeds_centers))]
        new_vertices, new_triangles = quick_replicate_meshes(seeds_centers,vertices,triangles)
        mesh = vertices_and_faces_to_mesh(new_vertices,new_triangles)

        a = anatomist.Anatomist()
        w3d = a.createWindow("3D")

        A_graph=a.toAObject(mesh)
        material = a.Material(diffuse=[1, 0, 0, 1])
        A_graph.setMaterial(material)
        w3d.addObjects(A_graph)
        return [w3d, A_graph]