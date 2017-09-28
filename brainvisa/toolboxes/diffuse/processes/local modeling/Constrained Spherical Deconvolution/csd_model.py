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
from joblib import dump, load
from dipy.reconst.csdeconv import ConstrainedSphericalDeconvModel
from brainvisa.diffuse.building_spheres import read_sphere
from brainvisa.diffuse.tools import shells, max_shell, is_multi_shell,select_outer_shell



userLevel = 0
name = 'Constrained Spherical Deconvolution (CSD) Model'
category = 'csd'

signature = Signature(
    'gradient_table', ReadDiskItem(
        'Gradient Table',
        'Joblib Pickle file'
    ),
    'single_fiber_response', ReadDiskItem(
        'Single Fiber Response',
        'Joblib Pickle File'
    ),
    'spherical_harmonic_order', Integer(),

    'regularization_sphere', ReadDiskItem(
        'Sphere Template',
        'GIFTI file'
    ),
    'regularization_weight', Float(),
    'positivity_threshold',Float(),
    'model', WriteDiskItem(
        'Constrained Spherical Deconvolution Model',
        'Joblib Pickle file'
    ),
)



def initialization(self):
    #init parameters
    self.regularization_weight = 1
    self.positivity_threshold = 0.1
    self.spherical_harmonic_order = 8
    #options
    self.setOptional('spherical_harmonic_order', 'regularization_weight', 'positivity_threshold',
                     'regularization_sphere')
    self.addLink('single_fiber_response','gradient_table')
    self.addLink('model','single_fiber_response')
    pass


def execution(self, context):
    gtab = load(self.gradient_table.fullPath())
    # Cheking that the gradient table is single shell else warning and keep only the outer shell
    context.warning("The DWI scheme for this data is multishell: bvalues", shells(gtab),". CSD implementation used only handle single shell DWI scheme. By default the higher shell bval",max_shell(gtab)," is selected" )

    if is_multi_shell(gtab):
        gtab = select_outer_shell(gtab)

    if self.regularization_sphere is None:
    #fixme: should be removed --> put a default value on the diskitem
        sphere = self.regularization_sphere
        context.write("No regularization sphere specified. The dipy default antipodally symmetric sphere of 362 vertices will be used. ")
    else:
        sphere = read_sphere(self.regularization_sphere.fullPath())


    rep = load(self.single_fiber_response.fullPath())
    csd = ConstrainedSphericalDeconvModel(gtab=gtab, response=rep, reg_sphere=sphere,
                                          sh_order=self.spherical_harmonic_order,
                                          lambda_=self.regularization_weight, tau=self.positivity_threshold)
    dump(csd, self.model.fullPath(), compress=9)


    #adding some metadata
    self.model.setMinf('model_type','csd')
    self.model.setMinf('gradient_table_uuid',self.gradient_table.uuid())
    self.model.setMinf('selected_shell', max_shell(gtab))
    self.model.setMinf('single_fiber_response_uuid',self.single_fiber_response.uuid())
    model_parameters = {'sh_order':self.spherical_harmonic_order, 'reg_weight':self.regularization_weight,
                         'positivity_threshold':self.positivity_threshold }
    self.model.setMinf('model_parameters', model_parameters)
    pass

