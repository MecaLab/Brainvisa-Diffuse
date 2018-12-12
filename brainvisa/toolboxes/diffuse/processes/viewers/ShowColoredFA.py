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

def validation():

    from distutils.spawn import find_executable as find_exec
    configuration = Application().configuration
    cmds = ['fsleyes']
    viewer = [find_exec(configuration.FSL.fsl_commands_prefix + cmd) for cmd in cmds]
    if not viewer[0]:
            raise ValidationError(_t_(
                ' FSL ' + ' fsleyes' + ' commandline could not be found. Check fsldir and fsl_command_prefix values into Brainvisa Preferences FSL menu !'))
    pass

from brainvisa.processes import *
from brainvisa.diffuse.tools import is_multi_shell
import joblib
import numpy as np


name = 'Anatomist Show Colored FA'
userLevel = 0
roles = ('viewer',)

signature = Signature(
  'fractionnal_anisotropy', ReadDiskItem(
        'Fractionnal Anisotropy Volume',
        'gz compressed NIFTI-1 image'
    ),
   'first_eigen_vector', ReadDiskItem(
        'First Eigen Vector Volume',
        'gz compressed NIFTI-1 image'
    ),
)

def initialization( self ):
    pass
    
def execution( self, context ):

    path_fa = self.fractionnal_anisotropy.fullPath()
    path_e1 = self.first_eigen_vector.fullPath()

    cmd = ['fsleyes', path_fa, path_e1, '-ot', 'rgbvector', '-mr', '0 1', '-mo', path_fa]
    context.system(*cmd)
