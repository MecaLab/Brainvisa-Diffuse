# -*-coding: utf-8 -*-

from brainvisa.processes import *
from brainvisa.diffuse.tools import array_to_vol
from copy import copy
from brainvisa.registration import getTransformationManager
from soma import aims
import numpy as np
from dipy.reconst.dti import TensorFit
from joblib import load


userLevel = 0

name = 'Diffusion Tensor Imaging (DTI) Derived Indices'


signature = Signature(
    'tensor_coefficients', ReadDiskItem(
        'Diffusion Tensor Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'tensor_model', ReadDiskItem(
        'Diffusion Tensor Model',
        'Joblib Pickle file'
    ),
    'fractionnal_anisotropy', WriteDiskItem(
        'Fractionnal Anisotropy Volume',
        'gz compressed NIFTI-1 image'
    ),
    'colored_fractionnal_anisotropy', WriteDiskItem(
        'Colored Fractionnal Anisotropy',
        'gz compressed NIFTI-1 image'
    ),
    'mean_diffusivity', WriteDiskItem(
        'Mean Diffusivity Volume',
        'gz compressed NIFTI-1 image'
    ),
    'first_eigen_vector', WriteDiskItem(
        'First Eigen Vector Volume',
        'gz compressed NIFTI-1 image'
    ),
    'second_eigen_vector', WriteDiskItem(
        'Second Eigen Vector Volume',
        'gz compressed NIFTI-1 image'
    ),
    'third_eigen_vector', WriteDiskItem(
        'Third Eigen Vector Volume',
        'gz compressed NIFTI-1 image'
    ),
    'evals', WriteDiskItem(
        'Eigen Values Volume',
        'gz compressed NIFTI-1 image'
    ),
    'advanced_indices', Boolean(),

    'axial_diffusivity', WriteDiskItem(
        'Axial Diffusivity Volume',
        'gz compressed NIFTI-1 image'#,
        #requiredAttributes={'map_type':'axial'}
    ),
    'planarity', WriteDiskItem(
        'Planarity Volume',
        'gz compressed NIFTI-1 image'#,
        #requiredAttributes={'map_type':'planarity'}
    ),
    'sphericity', WriteDiskItem(
        'Sphericity Volume',
        'gz compressed NIFTI-1 image'#,
        #requiredAttributes={'map_type':'sphericity'}
    ),
    'linearity', WriteDiskItem(
        'Linearity Volume',
        'gz compressed NIFTI-1 image'#,
        #requiredAttributes={'map_type':'linearity'}
    ),
    'mode', WriteDiskItem(
        'Mode Volume',
        'gz compressed NIFTI-1 image'#,
        #requiredAttributes={'map_type':'mode'}
    ),
)

def show_advanced_indices(self,dummy):
    signature = copy(self.signature)
    if self.advanced_indices :
        self.setEnable('axial_diffusivity','planarity','sphericity','linearity','mode')
        self.setOptional('axial_diffusivity', 'planarity', 'sphericity', 'linearity', 'mode')
    else:
        self.setOptional('axial_diffusivity', 'planarity', 'sphericity', 'linearity', 'mode')
        self.setHidden('axial_diffusivity','planarity','sphericity','linearity','mode')
    self.changeSignature(signature)
    tensor = getattr(self, 'tensor_coefficients')
    self._parameterHasChanged('tensor_coefficients', tensor)
    pass

def initialization( self ):
    self.advanced_indices = False
    self.addLink(None,'advanced_indices', self.show_advanced_indices)
    self.addLink('tensor_model','tensor_coefficients')
    self.addLink('fractionnal_anisotropy','tensor_coefficients')
    self.addLink('colored_fractionnal_anisotropy','tensor_coefficients')
    self.addLink('mean_diffusivity', 'tensor_coefficients')
    self.addLink('first_eigen_vector','tensor_coefficients')
    self.addLink('second_eigen_vector','first_eigen_vector')
    self.addLink('third_eigen_vector', 'first_eigen_vector')
    self.addLink('evals','tensor_coefficients')
    self.addLink('axial_diffusivity','tensor_coefficients')
    self.addLink('planarity', 'tensor_coefficients')
    self.addLink('sphericity', 'tensor_coefficients')
    self.addLink('linearity', 'tensor_coefficients')
    self.addLink('mode', 'tensor_coefficients')
    self.setHidden('tensor_model')
    self.setOptional('axial_diffusivity', 'planarity', 'sphericity', 'linearity', 'mode')

    pass




def execution( self, context ):

    tensor_coeff_vol = aims.read(self.tensor_coefficients.fullPath())
    tensor_coeff = np.asarray(tensor_coeff_vol)
    hdr = tensor_coeff_vol.header()

    tensor_model = load(self.tensor_model.fullPath())


    tenfit = TensorFit(tensor_model, tensor_coeff)
    #Mandatory parameters
    fa = tenfit.fa
    FA = array_to_vol(fa,hdr)
    aims.write(FA, self.fractionnal_anisotropy.fullPath())
    md = tenfit.md
    MD = array_to_vol( md ,hdr)
    aims.write(MD, self.mean_diffusivity.fullPath())
    evecs = tenfit.evecs
    vectors = [evecs[:,:,:,:,0], evecs[:,:,:,:,1], evecs[:,:,:,:,2]]
    evals = tenfit.evals




    eigen_values = array_to_vol(evals, hdr)
    aims.write(eigen_values, self.evals.fullPath())

    vectors_volume = [array_to_vol(v,hdr) for v in vectors]

    aims.write(vectors_volume[0], self.first_eigen_vector.fullPath())
    aims.write(vectors_volume[1], self.second_eigen_vector.fullPath())
    aims.write(vectors_volume[2], self.third_eigen_vector.fullPath())

    color_fa = tenfit.color_fa
    color_fa_vol = array_to_vol(color_fa)
    aims.write(color_fa_vol, self.colored_fractionnal_anisotropy.fullPath())
    # handling referentials
    transformManager = getTransformationManager()
    transformManager.copyReferential(self.tensor_coefficients, self.fractionnal_anisotropy)
    transformManager.copyReferential(self.tensor_coefficients, self.mean_diffusivity)
    # additionnal metadata
    self.mean_diffusivity.setMinf('tensor_coefficients_uuid', self.tensor_coefficients.uuid())
    self.fractionnal_anisotropy.setMinf('tensor_coefficients_uuid', self.tensor_coefficients.uuid())

    if self.advanced_indices:
        axial_diffusivity = tenfit.ad
        planarity = tenfit.planarity
        sphericity = tenfit.sphericity
        linearity = tenfit.linearity
        mode = tenfit.mode

        disk_items = [self.axial_diffusivity, self.planarity, self.sphericity, self.linearity, self.mode ]
        arrays = [axial_diffusivity, planarity, sphericity, linearity, mode]

        for ind, a in enumerate(arrays):
            vol = array_to_vol(a, hdr)
            aims.write(vol, disk_items[ind].fullPath())
            transformManager.copyReferential(self.tensor_coefficients, disk_items[ind])

    pass