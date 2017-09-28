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
import numpy
from soma import aims

name = 'Anatomist Show Q-space Sampling'
userLevel = 0
roles = ('viewer',)

def validation():
  anatomist.validation()
  
signature=Signature(
  'bvecs', ReadDiskItem('Gradient Directions', 'Text file' ),
  'bvals', ReadDiskItem( 'B values', 'Text file' ),
)

def initialization( self ):
    self.linkParameters( 'bvals', 'bvecs' )
    
def execution( self, context ):

    bvecs = numpy.loadtxt(self.bvecs.fullPath())
    bvals = numpy.loadtxt(self.bvals.fullPath())
    spheres_mesh_file = context.temporary(  'GIFTI file' )
    spheres_tex_file = context.temporary( 'Texture' )
    gen = aims.SurfaceGenerator()
    spheres_mesh = aims.AimsSurfaceTriangle()
    spheres_tex = aims.TimeTexture('FLOAT')
    for i in range(len(bvecs[0])):
        zoom_factor = bvals[i]/50
        sphere_size = bvals[i]/1000
        vec = zoom_factor*bvecs[:,i]
        spheres_mesh += gen.sphere(vec, sphere_size, 100)
        [spheres_tex[0].append(sphere_size) for i in range(100)]
    aims.write(spheres_mesh, spheres_mesh_file.fullPath())
    aims.write(spheres_tex, spheres_tex_file.fullPath())
    
    # zoom_factor = int(max(bvals)/50)
    big_sphere = context.temporary(  'GIFTI file' )
    # sphere = aims.AimsSurfaceTriangle()
    # sphere = gen.icosphere([0.0,0.0,0.0], zoom_factor, zoom_factor*10)
    tab=numpy.unique(bvals)
    tm1=0
    shell=[]
    sphere = aims.AimsSurfaceTriangle()
    for t in tab:
        if t-tm1<50:
            shell.append(t)
        else:
            radius = numpy.median(shell)/50
            shell = [t]
            sphere += gen.icosphere([0.0,0.0,0.0], radius, int(radius*10))
        tm1 = t
    radius = numpy.median(shell)/50
    sphere += gen.icosphere([0.0,0.0,0.0], radius, int(radius*10))
    aims.write(sphere, big_sphere.fullPath())

    
    a = anatomist.Anatomist()
    win = a.createWindow( 'Axial' )
    anamesh = a.loadObject( spheres_mesh_file.fullPath() )
    anatex = a.loadObject( spheres_tex_file.fullPath() )
    fusion2d = a.fusionObjects([anamesh, anatex], "FusionTexSurfMethod")
    win.addObjects(fusion2d )
##    anamesh.setMaterial( a.Material(diffuse = [0.0, 1.0, 1.0, 1]) )
    anamesh2 = a.loadObject( big_sphere.fullPath() )
    anamesh2.setMaterial( a.Material(diffuse = [0.3, 0.3, 0.3, 0.3], polygon_mode = 'wireframe') )
    win.addObjects(anamesh2 )
    
    return [win, fusion2d, anamesh2]
