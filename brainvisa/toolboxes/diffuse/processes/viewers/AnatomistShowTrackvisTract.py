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
from brainvisa.diffuse.streamlines import load_streamlines, bundle_to_mesh

name = 'Anatomist Show Streamlines'
roles = ( 'viewer', )
userLevel = 0

signature = Signature(
  'streamlines', ReadDiskItem( 'Streamlines', ['Trackvis tracts', 'Mrtrix streamlines'] ),
  'max_number', Integer()
)

def validation():
  anatomist.validation()

def initialization( self ):
  #self.setOptional('max_number')
  self.max_number = 30000
  pass

def execution( self, context ):

  #lazy load just to estimate the number of streamlines
  tractogram, header = load_streamlines(self.streamlines.fullPath(),lazy=True)
  #streamlines are in the LPI mm space
  nb_streamlines = header['nb_streamlines']
  streamlines = tractogram.streamlines
  if nb_streamlines > self.max_number:
    message = "The tractogram you try to display contains" +  str(nb_streamlines) + "streamlines\n In order to avoid memory crash only the first " +  self.max_number ," streamlines will be displayed"
    "If your computer crashes consider decreasing self.max_number value \n. On the contrary if you have enough memory to display the whole tractogram you may want to increase self.max_number value"
    context.write(message)
    bundle = [s for i, s in enumerate(streamlines) if i < self.max_number]
  else:
    bundle = list(streamlines)
  bundle_aims = bundle_to_mesh(bundle)
  del bundle

  a = anatomist.Anatomist()
  bundle_ana = a.toAObject(bundle_aims)
  bundle_ana.setMaterial(use_shader=1,shader_color_normals=1)

  del bundle_aims
  win = a.createWindow('3D')
  win.addObjects(bundle_ana)
  return [win, bundle_ana]

  
  
