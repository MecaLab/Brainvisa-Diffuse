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
from brainvisa.diffuse.tools import is_multi_shell
import joblib
import numpy as np


name = 'Anatomist Show Acquisition Info'
userLevel = 0
roles = ('viewer',)

signature = Signature(
  'gradient_table', ReadDiskItem(
        'Gradient Table',
        'Joblib Pickle file'
    ),
)

def initialization( self ):
    pass
    
def execution( self, context ):

   gtab = joblib.load(self.gradient_table.fullPath())
   bvals = gtab.bvals
   bvecs = gtab.bvecs
   gradients = gtab.gradients


   if is_multi_shell(gtab):
       msg = "Multi Shell Acquisition"
   else:
       msg = "Single Shell Acquisition"

   context.write("Minimal Information\n")
   context.write(msg)
   context.write(np.unique(bvals))

   context.write("Complete information\n")
   context.write("BO Threshold Used", gtab.b0_threshold)
   context.write("B Values", bvals)
   context.write("B Vectors", bvecs)
   context.write("Q Vectors", gradients)
   context.write("Big Delta", gtab.big_delta)
   context.write("Small Delta", gtab.small_delta)
