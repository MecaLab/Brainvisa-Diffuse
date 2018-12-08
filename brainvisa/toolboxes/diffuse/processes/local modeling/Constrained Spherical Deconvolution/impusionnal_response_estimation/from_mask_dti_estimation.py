
from brainvisa.processes import *
from brainvisa.diffuse.tools import vol_to_array, array_to_vol, array_to_mask,max_shell,is_multi_shell,shells,select_outer_shell
from soma import aims
import numpy as np
from joblib import load, dump
from dipy.reconst.dti import TensorFit, TensorModel
from dipy.reconst.csdeconv import response_from_mask, _get_response


userLevel = 2
name = 'Fiber Impulsionnal Response DTI Estimation'
category = 'Local_modeling'

signature = Signature(

    'diffusion_data', ReadDiskItem(
        'Corrected DW Diffusion MR',
        'Aims readable volume formats'
    ),
    'gradient_table', ReadDiskItem(
        'Gradient Table',
        'Joblib Pickle file'
    ),
    'tensor_model', ReadDiskItem(
        'Diffusion Tensor Model',
        'Joblib Pickle file'
    ),
    'tensor_coefficients', ReadDiskItem(
        'Diffusion Tensor Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
    'fa_threshold',Float(),
    'response', WriteDiskItem(
        'Single Fiber Response',
        'Joblib Pickle File'
    ),

)


def initialization ( self ):

    #linking
    self.addLink('gradient_table','diffusion_data')
    self.addLink('mask','diffusion_data')
    self.addLink('response','diffusion_data')
    self.setOptional('mask','tensor_model','tensor_coefficient','fa_theshold')
    #if this link works tensor_coefficient is found. will not work if several models or fit with different masks
    self.addLink('tensor_coefficients','diffusion_data')
    self.addLink('tensor_model','tensor_coefficient') #will work fo sure
    #setting values
    self.fa_threshold = 0.7 #default value used in Dipy tutorial
    #cosmetics
    pass



def execution( self , context ):

    #if an existing tensor has already been fitted dont compute a new one .
    if self.tensor_coefficients  is not None and self.tensor_model is not None:
        context.write('Fitted Tensor already exists ! Let s use it !')
        tensor_coeff_vol = aims.read(self.tensor_coefficients.fullPath())
        tensor_coeff = np.asarray(tensor_coeff_vol)
        hdr = tensor_coeff_vol.header()
        tensor_model = load(self.tensor_model.fullPath())
        tenfit = TensorFit(tensor_model, tensor_coeff)
        if self.mask is not None:
            mask_vol = aims.read(self.mask.fullPath())
            mask = vol_to_array(mask_vol)
            mask = array_to_mask(mask)
        else:
            context.write('No mask provided ! Estimating impulsionnal response from the whole volume or brain is not really accurate ! A default mask based on Fractionnal Anisotropy is  computed. ')
            fa = tenfit.fa
            # just to avoid nan is case of wrong fitting
            fa = np.clip(fa, 0, 1)
            #high FA vale is associated with single fiber direction voxel
            mask = fa > self.fa_threshold
            mask = mask.astype(bool)
        #code extracted from dipy  response_from_mask function
        sub_tenfit = tenfit[mask]
        lambdas = sub_tenfit.evals[:, :2]
        gtab = sub_tenfit.model.gtab
        vol = aims.read(self.diffusion_data.fullPath())
        data = np.asarray(vol)
        indices = np.where(mask)
        S0s = data[indices][:, np.nonzero(gtab.b0s_mask)[0]]
        response, ratio = _get_response(S0s, lambdas)

    else:
        context.write('No Tensor Fitted Yet! Compute a new one')

        gtab = load(self.gradient_table.fullPath())

        if is_multi_shell(gtab):
            context.warning("The DWI scheme for this data is multishell: bvalues", shells(gtab),
                        ". CSD implementation used in Diffuse currently only handle single shell DWI scheme. By default the higher shell bval",
                            max_shell(gtab), " is selected")
            context.warning("Even if only the outer shell is use for deconvolution, the following estimation method will use the full DWI scheme for response estimation. It might be inaccurate  if the deconvolved shell bvalue is too high (b5000)")

        vol = aims.read(self.diffusion_data.fullPath())
        data = np.asarray(vol)

        if self.mask is not None:
            mask_vol = aims.read(self.mask.fullPath())
            mask = vol_to_array(mask_vol)
            mask = array_to_mask(mask)
            response, ratio = response_from_mask(gtab, data, mask)
        else:
            context.warning("No mask provided ! Compute a high-FA based mask with threshold" + str(self.th))
            #default tensor model --> we dont store it for now
            tensor = TensorModel(gtab)
            #whole volume fit
            tenfit = tensor.fit(data)
            fa = tenfit.fa
            # just to avoid nan is case of wrong fitting
            fa = np.clip(fa, 0, 1)
            # high FA vale is associated with single fiber direction voxel
            mask = fa > self.fa_threshold
            mask = mask.astype(bool)
            # code extracted from dipy  response_from_mask function
            sub_tenfit = tenfit[mask]
            lambdas = sub_tenfit.evals[:, :2]
            gtab = sub_tenfit.model.gtab
            vol = aims.read(self.diffusion_data.fullPath())
            data = np.asarray(vol)
            indices = np.where(mask)
            S0s = data[indices][:, np.nonzero(gtab.b0s_mask)[0]]
            response, ratio = _get_response(S0s, lambdas)

    #store the response
    dump(response, self.response.fullPath())






