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

include('base')
default_response = 'default_response'
default_model = 'default_model'
default_fit = 'brain_fit'

insert( '{center}/{subject}',
  'dmri', SetContent( 
    '{acquisition}', SetDefaultAttributeValue( 'acquisition', default_acquisition ), SetContent(
      'raw_dwi_referential_<subject>', SetType( 'Referential of Raw DW Diffusion MR' ),
      'raw_dwi_<subject>', SetType( 'Raw Diffusion MR'),
      'raw_dwi_<subject>', SetType( 'Diffusion Acquisition Metadata'),
      'sigma_noise_<subject>', SetType( 'Noise Standard Deviation'),
      'denoised_dwi_<subject>', SetType( 'Denoised Diffusion MR'),
      'raw_bvecs_<subject>', SetType( 'Raw B Vectors'),
      'raw_bvals_<subject>', SetType( 'Raw B Values'),
      'reoriented_bvecs_<subject>', SetType('Reoriented B Vectors'),
      'blip_reversed_dwi_<subject>', SetType( 'Blip Reversed DW Diffusion MR'),
      'blip_reversed_dwi_<subject>',  SetType( 'Blip Reversed Diffusion Acquisition Metadata'),
      'fieldmap_rads_<subject>', SetType( 'Fieldmap Phase'),
      'fieldmap_abs_<subject>', SetType('Fieldmap Magnitude'),
    ),
  ),
)

insert( '{center}/{subject}/dmri/{acquisition}',
  '{analysis}', SetDefaultAttributeValue( 'analysis', default_analysis ), SetContent(
    'eddy_corrected_dwi_<subject>', SetType( 'EC corrected DW Diffusion MR' ),
    'corrected_dwi_<subject>', SetType( 'Unwarped DW Diffusion MR' ), SetPriorityOffset(+2) ,
    'corrected_bvecs_<subject>', SetType( 'Corrected B Vectors' ),
    'gradient_table',SetType('Gradient Table'),
    'b0_<subject>', SetType( 'B0 Volume' ),
    'b0_brain_<subject>', SetType( 'B0 Volume Brain' ),
    'b0_brain_mask_<subject>', SetType( 'B0 Volume Brain Mask' ),
    'b0_to_T1_<subject>', SetType( 'DW Diffusion MR to T1 MRI' ),
    'T1_to_dwi_<subject>', SetType( 'T1 MRI to DW Diffusion MR' ),
    'T1_to_dwi_mask_<subject>', SetType( 'T1 MRI to DW Diffusion MR Brain' ),
    'WM_mask_<subject>', SetType( 'T1 MRI to DW Diffusion MR WM' ),
    'GM_mask_<subject>', SetType( 'T1 MRI to DW Diffusion MR GM' ),
    'skeleton_mask_<subject>', SetType( 'T1 MRI to DW Diffusion MR Skeleton' ),
    #useful to provide more accurate tractography constraints
    'CSF_pve_dwi_<subject>', SetType( 'CSF PVE Diffusion MR'),
    'WM_pve_dwi_<subject>', SetType( 'WM PVE Diffusion MR'),
    'GM_pve_dwi_<subject>', SetType( 'GM PVE Diffusion MR'),
  ),
)

insert( '{center}/{subject}/dmri/{acquisition}/{analysis}',
  'FSL_preprocessing', SetType( 'Preprocessing Directory' ), SetContent(
    'fieldmap_rads_brain_<subject>', SetType( 'Fieldmap Phase Brain' ),
    'fieldmap_abs_brain_<subject>', SetType( 'Fieldmap Magnitude Brain' ),
    'fieldmap_abs_brain_<subject>_mask', SetType( 'Fieldmap Magnitude Mask' ),
    'fieldmap_abs_warped_<subject>', SetType( 'Fieldmap Magnitude Warped' ),
    'fieldmap_abs_warped_to_dwi_<subject>', SetType( 'Fieldmap Magnitude Warped Reg' ),
    'fieldmap_to_dwi_<subject>', SetType( 'Fieldmap to DW Mat' ),
    'fieldmap_rads_brain_to_dwi_<subject>', SetType( 'Fieldmap Phase Reg' ),
    'fieldmap_abs_warped_to_dwi_brain_<subject>', SetType( 'Fieldmap Magnitude Warped Brain Reg' ),
    'fieldmap_abs_warped_to_dwi_brain_<subject>_mask', SetType( 'Fieldmap Magnitude Warped Mask Reg' ),
    'b0_volumes_<subject>', SetType( 'Blip Reversed B0 Volumes' ),
    'topup_b0_<subject>', SetType( 'Blip Reversed Unwarped B0 Volumes' ),
    'b0_mean_<subject>', SetType( 'Blip Reversed B0 Mean' ),
    'b0_mean_brain_<subject>', SetType( 'Blip Reversed B0 Mean Brain' ),
    'b0_mean_brain_<subject>_mask', SetType( 'Blip Reversed B0 Mean Mask' ),
    'acq_parameters_<subject>', SetType( 'Blip Reversed Parameters' ),
    'acq_index_<subject>', SetType( 'Blip Reversed Index' ),
    'up_down_data_<subject>', SetType( 'Blip Reversed Data' ),
    'up_down_bvals_<subject>', SetType( 'Blip Reversed B Values' ),
    'up_down_bvecs_<subject>', SetType( 'Blip Reversed B Vectors' ),
  ),
)

insert( '{center}/{subject}/dmri/{acquisition}/{analysis}',
  'registration', SetContent(
    'dwi_TO_T1_<subject>', SetType( 'Transform Diffusion MR to T1 MRI' ),
    'T1_TO_dwi_<subject>', SetType( 'Transform T1 MRI to Diffusion MR' ),
    'dwi_TO_T1_dfm_field_<subject>', SetType( 'NL Deform Diffusion MR to T1 MRI' ),
    'T1_TO_dwi_dfm_field_<subject>', SetType( 'NL Deform T1 MRI to Diffusion MR' ),
  ),
)

insert( '{center}/{subject}/dmri/{acquisition}/{analysis}',
  'mesh', SetContent(
    '<subject>_Lwhite_to_dwi', SetType( 'Left Registered White Mesh' ), SetWeakAttr( 'side', 'left' ),
    '<subject>_Rwhite_to_dwi', SetType( 'Right Registered White Mesh' ), SetWeakAttr( 'side', 'right' ),
    '<subject>_Lhemi_to_dwi', SetType( 'Left Registered Hemisphere Mesh' ), SetWeakAttr( 'side', 'left' ),
    '<subject>_Rhemi_to_dwi', SetType( 'Right Registered Hemisphere Mesh' ), SetWeakAttr( 'side', 'right' ),
  ),
)

insert( '{center}/{subject}/dmri/{acquisition}/{analysis}',
  'seeds', SetContent(
   '*_LPI_voxel_space', SetType('Seeds'),
    ),
)



######BEGINNING OF LOCAL MODEL AND TRACTOGRAPHY ONTOLOGY##########
#MODEL FAMILIES : FOR NOW DTI AND CSD


insert('{center}/{subject}/dmri/{acquisition}/{analysis}/dti',
  '{model}', SetFileNameStrongAttribute('model'), SetWeakAttr('model_type', 'dti'),SetDefaultAttributeValue( 'model', default_model),SetContent(
     '<subject>_<acquisition>_dti_<model>', SetType('Diffusion Tensor Model'),
     '{model_fit}', SetFileNameStrongAttribute('model_fit'),SetDefaultAttributeValue( 'model_fit', default_fit), SetContent(),
     'diffusion_odf', SetContent(),
  ),
)

insert('{center}/{subject}/dmri/{acquisition}/{analysis}/dti/{model}',
  '{model_fit}', SetContent(
        '<subject>_tensor_coefficients', SetType('Diffusion Tensor Coefficients'),
        'derived_indices', SetContent(
            '<subject>_fractionnal_anisotropy', SetType('Fractionnal Anisotropy Volume'),
            '<subject>_colored_fractionnal_anisotropy', SetType('Colored Fractionnal Anisotropy'),
            '<subject>_mean_diffusivity', SetType('Mean Diffusivity Volume'),
            '<subject>_apparent_diffusion_coefficient', SetType('Apparent Diffusion Coefficient Volume'),
            '<subject>_first_eigen_vector', SetType('First Eigen Vector Volume'),
            '<subject>_second_eigen_vector', SetType('Second Eigen Vector Volume'),
            '<subject>_third_eigen_vector', SetType('Third Eigen Vector Volume'),
            '<subject>_eigen_values', SetType('Eigen Values Volume'),
            '<subject>_axial_diffusivity', SetType('Axial Diffusivity Volume'),
            '<subject>_planarity', SetType('Planarity Volume'),
            '<subject>_sphericity', SetType('Sphericity Volume'),
            '<subject>_linearity', SetType('Linearity Volume'),
            '<subject>_geodesic_diffusivity', SetType('Geodesic Diffusivity Volume'),
            '<subject>_mode', SetType('Mode Volume'),
            '<subject>_predicted_signal',SetType('DTI Predicted Signal'),
            '<subject>_residuals', SetType('DTI Residuals'),
        ),
        'diffusion_odf', SetContent(
            'sh_coefficients',SetType('Spherical Harmonics Coefficients'),
            ),
            '{odf_instance}', SetContent(
                'odf', SetType('Orientation Distribution Function'),
            ),
        ),
)


insert('{center}/{subject}/dmri/{acquisition}/{analysis}/csd',
       '{fiber_response}', SetFileNameStrongAttribute('fiber_response'),SetDefaultAttributeValue( 'fiber_response', default_response), SetContent(
        '<subject>_wm_fiber_response', SetType('Single Fiber Response'),
    ),
)

insert('{center}/{subject}/dmri/{acquisition}/{analysis}/csd/{fiber_response}',
       '{model}',SetWeakAttr('model_type','csd'), SetFileNameStrongAttribute('model'),SetDefaultAttributeValue( 'model', default_model), SetContent(
        '<model>', SetType('Constrained Spherical Deconvolution Model'),
        '{model_fit}', SetFileNameStrongAttribute('model_fit'), SetDefaultAttributeValue( 'model_fit', default_fit), SetContent(
                'derived_indices', SetContent(
                    '<subject>_generalized_fractionnal_anisotropy', SetType('Generalized Fractionnal Anisotropy Volume'),
                    '<subject>_mean_diffusivity', SetType('Mean Diffusivity Volume'),
                    '<subject>_predicted_signal',SetType('CSD Predicted Signal'),
                    '<subject>_residuals', SetType('CSD Residuals'),
                ),
                'fiber_odfs', SetContent(
                    'sh_coefficients', SetType('Spherical Harmonics Coefficients'),
                    '{odf_instance}', SetContent(
                        'odf_volume', SetType('Orientation Distribution Function'),
                        'odf_mesh', SetType('Spherical Function Mesh'),
                        'odf_texture', SetType('Spherical Function Texture'),
                            ),
                    
                    ),
                ),
         ),
)

insert('{center}/{subject}/dmri/{acquisition}/{analysis}/global_tracking',
    'gibbs_tracking', SetContent(
        '<subject>_global_streamlines', SetType('Streamlines'),
        '<subject>_density_map', SetType('Streamlines Density Map'),
    ),
)

insert('{center}/{subject}/dmri/{acquisition}/{analysis}/tractography',
    '{tracking_session}', SetContent(
         '<subject>_<analysis>_<tracking_session>_streamlines', SetType('Streamlines'),
         '<subject>_<analysis>_<tracking_session>_density_map', SetType('Streamlines Density Map'), SetType('Streamlines Density Map'),
	),
)


