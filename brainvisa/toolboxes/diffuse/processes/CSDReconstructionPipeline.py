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



userLevel = 1
name = 'CSD Pipeline'
category = 'pipeline'

signature = Signature(

    'diffusion_data', ReadDiskItem(
        'Corrected DW Diffusion MR',
        'Aims readable volume formats'
    ),
    'impulsionnal_fiber_response', WriteDiskItem(
        'Single Fiber Response',
        'Joblib Pickle File'
    ),
    'model', WriteDiskItem(
    'Constrained Spherical Deconvolution Model',
    'Joblib Pickle file'
    ),
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
    'FOD_sh_coeff', WriteDiskItem(
        'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'FOD',WriteDiskItem(
        'Orientation Distribution Function',
        'gz compressed NIFTI-1 image'
    ),
)




def initialization(self):

    eNode = SerialExecutionNode( self.name, parameterized=self )

    eNode.addChild('GradientTable',
                   ProcessExecutionNode('GradientTableConstruction', optional=True))

    eNode.addChild('FiberResponse',
                   ProcessExecutionNode('recursive_estimation', optional=True))

    eNode.addChild('Model',
                   ProcessExecutionNode('csd_model', optional=True))

    eNode.addChild('Reconstruction',
                                      ProcessExecutionNode('csd_fitting', optional=True, selected=True))


    eNode.addChild('Indices',
                   ProcessExecutionNode('csd_derived_indices', optional=True,
                                        selected=True))
    eNode.addChild('ODF',
                    ProcessExecutionNode('csd_odf', optional=True,
                                        selected=False))
    eNode.addChild('Prediction',
                   ProcessExecutionNode('csd_signal_prediction',optional=True,
                                        selected=False))




    #change signature of related process
    self.addLink('impulsionnal_fiber_response','diffusion_data')
    self.addLink('model','impulsionnal_fiber_response')
    self.addLink('mask', 'diffusion_data')
    self.addLink('FOD_sh_coeff','model')
    self.addLink('FOD', 'FOD_sh_coeff')
    self.setOptional('FOD','mask')
    #classical links to insure all parameters can be changed (rem Links can have funny behavior)


    #GradientTable process links
    eNode.addLink('GradientTable.diffusion_data', 'diffusion_data')

    #FiberResponse process links
    eNode.removeLink('FiberResponse.response', 'FiberResponse.diffusion_data')
    eNode.removeLink('FiberResponse.gradient_table','FiberResponse.diffusion_data')
    eNode.removeLink('FiberResponse.mask', 'FiberResponse.diffusion_data')
    eNode.addLink('FiberResponse.diffusion_data','GradientTable.diffusion_data')
    eNode.addLink('FiberResponse.gradient_table','GradientTable.gradient_table')
    eNode.addLink('FiberResponse.mask','mask')
    eNode.addLink('FiberResponse.response','impulsionnal_fiber_response')

    #Model process links
    eNode.Model.removeLink('single_fiber_response','gradient_table')
    eNode.Model.removeLink('model','single_fiber_response')
    eNode.addLink('Model.gradient_table','GradientTable.gradient_table')
    eNode.addLink('Model.single_fiber_response','impulsionnal_fiber_response')
    eNode.addLink('Model.model','model')



     #Full Reconstruction pipeline
    eNode.Reconstruction.removeLink('csd_model', 'diffusion_data')
    eNode.Reconstruction.removeLink('mask', 'diffusion_data')
    eNode.Reconstruction.removeLink('fibre_odf_sh_coeff', 'csd_model')

       #Fit
    eNode.addLink('Reconstruction.diffusion_data','diffusion_data')
    eNode.addLink('Reconstruction.csd_model','model')
    eNode.addLink('Reconstruction.mask','mask')
    eNode.addLink('Reconstruction.fibre_odf_sh_coeff','FOD_sh_coeff')
      #Derived Indices
    eNode.Indices.removeLink('csd_model','fibre_odf_sh_coeff')
    eNode.Indices.removeLink('mask', 'fibre_odf_sh_coeff')
    eNode.Indices.removeLink('generalized_fractionnal_anisotropy', 'fibre_odf_sh_coeff')

    eNode.addLink('Indices.fibre_odf_sh_coeff', 'FOD_sh_coeff')
    eNode.addLink('Indices.csd_model', 'FOD_sh_coeff')
    eNode.addLink('Indices.mask','mask')
    eNode.addLink('Indices.generalized_fractionnal_anisotropy', 'FOD_sh_coeff')


    # ODF
    eNode.ODF.removeLink('csd_model', 'fibre_odf_sh_coeff')
    eNode.ODF.removeLink('mask', 'fibre_odf_sh_coeff')
    eNode.ODF.removeLink('fibre_odf', 'fibre_odf_sh_coeff')

    eNode.addLink('ODF.fibre_odf_sh_coeff', 'FOD_sh_coeff')
    eNode.addLink('ODF.mask','mask')
    eNode.addLink('ODF.fibre_odf', 'FOD' )

    #Signal Prediction
    eNode.Prediction.removeLink('csd_model', 'fibre_odf_sh_coeff')
    eNode.Prediction.removeLink('mask', 'fibre_odf_sh_coeff')
    eNode.Prediction.removeLink('S0_signal', 'fibre_odf_sh_coeff')
    eNode.Prediction.removeLink('predicted_signal', 'fibre_odf_sh_coeff')
    eNode.addLink('Prediction.fibre_odf_sh_coeff', 'FOD_sh_coeff')
    eNode.addLink('Prediction.csd_model', 'FOD_sh_coeff')
    eNode.addLink('Prediction.mask', 'mask')
    eNode.addLink('Prediction.S0_signal', 'FOD_sh_coeff')
    eNode.addLink('Prediction.predicted_signal', 'FOD_sh_coeff')





    self.setExecutionNode(eNode)
