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
# knowledge of the CeCILL license version 2 and that you accept its
#terms.


from brainvisa.processes import *
from copy import copy



userLevel = 0
name = '2.a DTI Pipeline'
category = 'dti pipeline'

signature = Signature(

    'diffusion_data', ReadDiskItem(
        'Corrected DW Diffusion MR',
        'Aims readable volume formats'
    ),
    'fitting_method', Choice(('Weigthed Least Square','WLS'),
                     ('Least Square', 'LS'),
                     ('Non Linear Least Square', 'NNLS'),
                     ),
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
    'tensor_model', WriteDiskItem(
    'Diffusion Tensor Model',
    'Joblib Pickle file'
    ),
    'tensor_coefficients', WriteDiskItem(
        'Diffusion Tensor Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    # 'compute_odf', Boolean(),
    # 'd-odf',WriteDiskItem(
    #     'Orientation Distribution Function',
    #     'gz compressed NIFTI-1 image'
    # ),
)

# def switch_odf_computation(self, eNode):
#     signature = copy(self.signature)
#     if self.compute_odf:
#         self.setEnable('d-odf')
#         #eNode.ODF.setSelected(True)
#     else:
#         self.setOptional('d-odf')
#         self.setHidden('d-odf')
#         #eNode.ODF.setSelected(False)
#     self.changeSignature(signature)




def initialization(self):

    #Pipeline GRAPH
    eNode = SerialExecutionNode( self.name, parameterized=self )

    eNode.addChild('GradientTable',
                   ProcessExecutionNode('GradientTableConstruction',optional=True))

    eNode.addChild('Model',
                   ProcessExecutionNode('DTI_tensor_model', optional=True))

    eNode.addChild('Reconstruction',
                   ProcessExecutionNode( 'DTI_fitting',optional=True))

    eNode.addChild('Indices',
                    ProcessExecutionNode('DTI_derived_indices',
                                                     optional=True,
                                                     selected=True))
    eNode.addChild('SignalPrediction',
                   ProcessExecutionNode('DTI_signal_prediction',
                                        optional=True,
                                        selected=False))
    # eNode.addChild('ODF',
    #                  ProcessExecutionNode('DTI_ODF',
    #                                      optional=True,
    #                                       selected=False))

    self.setExecutionNode(eNode)



    #LINKINGS
    self.addLink('mask','diffusion_data')
    self.addLink('tensor_coefficients','tensor_model')
    self.setOptional('mask')

    #GradientTable process links
    # eNode.GradientTable.removeLink('corrected_dwi_volume', 'bvecs')
    # eNode.GradientTable.addLink('bvecs','corrected_dwi_volume')
    eNode.addLink('GradientTable.diffusion_data','diffusion_data')

    #Model process link
    eNode.Model.removeLink('model','gradient_table')
    eNode.addLink('Model.gradient_table','GradientTable.gradient_table')
    eNode.addLink('Model.method','fitting_method')
    eNode.Model.setHidden('method')
    eNode.addLink('tensor_model','Model.gradient_table')
    eNode.addLink('Model.model','tensor_model')

         #Fitting Subpart
    eNode.Reconstruction.removeLink('tensor_model', 'diffusion_data')
    eNode.Reconstruction.removeLink('mask', 'diffusion_data')
    eNode.Reconstruction.removeLink('tensor_coefficients', 'tensor_model')
    eNode.addLink('Reconstruction.diffusion_data','diffusion_data')
    eNode.addLink('Reconstruction.tensor_model','tensor_model')
    eNode.addLink('Reconstruction.mask','mask')
    eNode.addLink('Reconstruction.tensor_coefficients','tensor_coefficients')

    #
    #     #Derived Indices
    eNode.Indices.removeLink('tensor_model', 'tensor_coefficients')
    eNode.addLink('Indices.tensor_coefficients','tensor_coefficients')
    eNode.addLink('Indices.tensor_model','tensor_model')

    #----#ODF extraction :
    # eNode.ODF.removeLink('tensor_model','tensor_coefficients')
    # eNode.ODF.removeLink('d-odf', 'tensor_coefficients')
    # eNode.addLink('ODF.tensor_coefficients','tensor_coefficients')
    # eNode.addLink('ODF.d-odf', 'd-odf')

    #----#Prediction Signal :
    eNode.SignalPrediction.removeLink('tensor_model','tensor_coefficients')

    # eNode.addLink('SignalPrediction.tensor_model','tensor_model')
    eNode.addLink('SignalPrediction.tensor_model', 'tensor_model')
    eNode.addLink('SignalPrediction.tensor_coefficients', 'tensor_coefficients')
























