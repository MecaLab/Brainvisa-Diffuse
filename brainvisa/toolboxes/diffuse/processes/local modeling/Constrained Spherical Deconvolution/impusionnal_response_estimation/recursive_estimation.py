
from brainvisa.processes import *
from brainvisa.diffuse.tools import vol_to_array, array_to_vol, array_to_mask,max_shell,is_multi_shell,shells,select_outer_shell
from brainvisa.diffuse.building_spheres import read_sphere
from dipy.reconst.csdeconv import recursive_response
from dipy.core.gradients import gradient_table_from_bvals_bvecs
from dipy.data import get_sphere
from soma import aims
import numpy as np
from joblib import load, dump


userLevel = 0
name = 'Recursive Estimation'
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
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
    'sphere',ReadDiskItem(
        'Sphere Template',
        'Gifti File'
    ),
    'sh_order', Integer(),
    'initial_fa',Float(),
    'initial_trace',Float(),
    'peak_threshold',Float(),
    'nb_iter',Integer(),
    'convergence_rate',Float(),
    'response', WriteDiskItem(
        'Single Fiber Response',
        'Joblib Pickle File'
    ),

)


def initialization ( self ):
    #default dipy values
    self.sh_order = 8
    self.initial_fa = 0.08
    self.initial_trace = 0.0021
    self.peak_threshold = 0.01
    self.nb_iter = 8
    self.convergence_rate = 0.001
    self.setOptional('mask','sphere')

    #linking
    self.addLink('gradient_table','diffusion_data')
    self.addLink('mask','diffusion_data')
    self.addLink('response','diffusion_data')
    pass


def execution( self , context ):
    #loading light objects first
    gtab = load(self.gradient_table.fullPath())
    if self.sphere is not None:
        sphere = read_sphere(self.sphere.fullPath())
    else:
        context.write('No sphere provided. The default dipy sphere symmetric 362 will be used')
        sphere = get_sphere()

    if is_multi_shell(gtab):
        context.warning("The DWI scheme for this data is multishell: bvalues", shells(gtab),
                    ". CSD implementation used only handle single shell DWI scheme. By default the higher shell bval",
                        max_shell(gtab), " is selected")
        max_value = max_shell(gtab)
        #In this cas we physically select the data it migh be faster and cleaner
        index = np.logical_or(gtab.bvals==max_value, gtab.bvals==0)
        nbvals ,nbvecs = gtab.bvals[index], gtab.bvecs[index]
        ngtab = gradient_table_from_bvals_bvecs(nbvals,nbvecs)

        vol = aims.read(self.diffusion_data.fullPath())
        data = np.asarray(vol)
        context.write("Initial diffusion data shape", data.shape)
        data = data[:,:,:,index]
        context.write("Diffusion data shape after outer shell selection",data.shape)
        gtab = ngtab
    else:
        vol = aims.read(self.diffusion_data.fullPath())
        data = np.asarray(vol)

    mask_vol = aims.read(self.mask.fullPath())
    mask = vol_to_array(mask_vol)
    mask = array_to_mask(mask)

    response = recursive_response(gtab, data, mask, sh_order=np.int16(self.sh_order),peak_thr=self.peak_threshold,init_fa=self.initial_fa,init_trace=self.initial_trace,iter=np.int16(self.nb_iter),convergence=self.convergence_rate,sphere=sphere, parallel=False,nbr_processes=1)

    dump(response, self.response.fullPath())






