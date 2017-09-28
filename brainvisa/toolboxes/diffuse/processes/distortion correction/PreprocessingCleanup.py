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

name = 'Preprocessing Files Cleanup'
userLevel = 1

signature=Signature(
    'Preprocessing_directory', ReadDiskItem( 'Preprocessing Directory', 'Directory' ),
)

def execution( self, context ):

    # analysis_directory = os.path.dirname(self.corrected_data.fullPath())
    # FSL_directory = analysis_directory + '/FSL_preprocessing'
    FSL_directory = self.Preprocessing_directory.fullPath()

    result = context.ask("<p><b>WARNING: All the files contained in the following directory will be deleted: " + FSL_directory + ". Are you sure you want to continue ? <b></p>", "yes", "no")
    # result = 0
    if result == 0:
        context.system('rm', '-rf', FSL_directory)
        context.write('Cleanup done !')
    else:
        context.write('Cleanup canceled')
