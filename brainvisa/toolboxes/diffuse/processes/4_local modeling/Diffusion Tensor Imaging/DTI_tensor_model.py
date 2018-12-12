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
from joblib import load, dump
from dipy.reconst.dti import TensorModel


userLevel = 0
name = 'Diffusion Tensor Imaging (DTI) Model'


signature = Signature(
    'gradient_table', ReadDiskItem(
        'Gradient Table',
        'Joblib Pickle file'
    ),

    'method', Choice(('Weigthed Least Square','WLS'),
                     ('Least Square', 'LS'),
                     ('Non Linear Least Square', 'NLLS'),
                     ),
    'model', WriteDiskItem(
    'Diffusion Tensor Model',
    'Joblib Pickle file'
    ),
)



def initialization(self):

    self.method = 'WLS'
    self.addLink( 'model', 'gradient_table' )


def execution(self, context):

    gtab = load(self.gradient_table.fullPath())
    tensor = TensorModel(gtab, fit_method=self.method)
    dump(tensor, self.model.fullPath(), compress=9)
    #handling metadata:
    self.model.setMinf('gradient_table',self.gradient_table.uuid())
    self.model.setMinf('fitting_method', self.method)
    self.model.setMinf('model_type','dti')
    context.write("Process finish successfully")

