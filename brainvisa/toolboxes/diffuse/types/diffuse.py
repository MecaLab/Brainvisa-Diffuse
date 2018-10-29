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

include( 'builtin' )
include( 'anatomy' )
include( 'registration' )


#--------------------------------Acquisition Scheme Informations: B Vectors and Intensities-------------------|

Format( 'BValues format', 'f|*.bval' )
Format( 'BVectors format', 'f|*.bvec' )

createFormatList(
  'BValues',
  (
    'BValues format',
    'Text File',
  )
)

createFormatList(
  'BVectors',
  (
    'BVectors format',
    'Text File',
  )
)

FileType( 'B Values','Any Type','BValues')
FileType( 'Raw B Values', 'B Values' )
FileType( 'Blip Reversed B Values', 'B Values' )

FileType( 'B Vectors','Any Type','BVectors')
FileType( 'Raw B Vectors','B Vectors' )
FileType( 'Blip Reversed B Vectors', 'B Vectors' )
FileType( 'Reoriented B Vectors', 'B Vectors' )
FileType( 'Corrected B Vectors', 'B Vectors' )

#-----------------------------------------------------------------------------------------------------------------------|


#--------------------------------------Diffusion Volume Preprocessing Stage --------------------------------------------|

FileType( 'Preprocessing Directory', 'Directory' )

FileType( 'Diffusion MR', '4D Volume' )
FileType( 'Blip Reversed DW Diffusion MR', 'Diffusion MR' )
FileType( 'Raw Denoised Diffusion MR', 'Diffusion MR' )
FileType( 'Raw Diffusion MR', 'Raw Denoised Diffusion MR')
FileType( 'Denoised Diffusion MR', 'Raw Denoised Diffusion MR')

FileType( 'Noise Standard Deviation', '3D Volume')

FileType('Diffusion ROI', 'ROI')
FileType('Diffusion MR Mask','Diffusion ROI')

FileType( 'Corrected DW Diffusion MR', 'Diffusion MR' )
FileType( 'Unwarped DW Diffusion MR', 'Corrected DW Diffusion MR' )
FileType( 'EC corrected DW Diffusion MR', 'Corrected DW Diffusion MR' )

#-----------------------------------------------------BOS(T2)----------------------------------------------------------|

FileType( 'B0 Diffusion MR', '3D Volume' )
FileType( 'B0 Volume', 'B0 Diffusion MR' )
FileType( 'B0 Volume Brain', 'B0 Diffusion MR' )
FileType( 'B0 Volume Brain Mask', 'Diffusion MR Mask' )
FileType( 'B0 Volume Unwarped', 'B0 Diffusion MR' )


#--------------Handling Additionnal Acquisitions------------------------------------------------------------------------|
#Fieldmap
FileType( 'Fieldmap', '3D Volume' )
FileType( 'Fieldmap Phase', 'Fieldmap' )
FileType( 'Fieldmap Phase Brain', 'Fieldmap' )
FileType( 'Fieldmap Magnitude', 'Fieldmap' )
FileType( 'Fieldmap Magnitude Brain', 'Fieldmap' )
FileType( 'Fieldmap Magnitude Mask', 'Diffusion MR Mask')
FileType( 'Fieldmap Magnitude Warped', 'Fieldmap' )
FileType( 'Fieldmap Magnitude Warped Reg', 'Fieldmap' )
FileType( 'Fieldmap Phase Reg', 'Fieldmap' )
FileType( 'Fieldmap Magnitude Warped Brain Reg', 'Fieldmap' )
FileType( 'Fieldmap Magnitude Warped Mask Reg', 'Diffusion MR Mask' )

#Reversed phase encoding acquisition
FileType( 'Blip Reversed B0 4D', '4D Volume' )
FileType( 'Blip Reversed B0 Volumes', 'Blip Reversed B0 4D' )
FileType( 'Blip Reversed Unwarped B0 Volumes', 'Blip Reversed B0 4D' )
FileType( 'Blip Reversed B0', '3D Volume' )
FileType( 'Blip Reversed B0 Mean', 'Blip Reversed B0' )
FileType( 'Blip Reversed B0 Mean Brain', 'Blip Reversed B0' )
FileType( 'Blip Reversed B0 Mean Mask', 'Diffusion MR Mask' )
FileType( 'Blip Reversed Parameters', 'Text file' )
FileType( 'Blip Reversed Index', 'Text file' )
FileType( 'Blip Reversed Data', '4D Volume' )
FileType( 'Blip Reversed Bvalues', 'B values' )
FileType( 'Blip Reversed B Vectors', 'B Vectors' )

#----------------- Registration -------------------------
FileType( 'Referential of Raw DW Diffusion MR', 'Referential' )

FileType( 'Transformation Matrix', 'Text file' )
FileType( 'Fieldmap to DW Mat', 'Transformation Matrix' )
FileType( 'Transform Diffusion MR to T1 MRI', 'Transformation matrix' )
FileType( 'Transform T1 MRI to Diffusion MR', 'Transformation matrix' )
FileType( 'Deformation Field', '3D Volume')
FileType( 'NL Deform Diffusion MR to T1 MRI', 'Deformation Field')
FileType( 'NL Deform T1 MRI to Diffusion MR', 'Deformation Field')

FileType( 'DW Diffusion MR to T1 MRI', '3D Volume' )
FileType( 'T1 MRI to DW Diffusion MR', '3D Volume' )
FileType( 'T1 MRI to DW Diffusion MR Mask', 'Diffusion MR Mask' )
FileType( 'T1 MRI to DW Diffusion MR Brain', 'T1 MRI to DW Diffusion MR Mask' )
FileType( 'T1 MRI to DW Diffusion MR GM', 'T1 MRI to DW Diffusion MR Mask' )
FileType( 'T1 MRI to DW Diffusion MR WM', 'T1 MRI to DW Diffusion MR Mask' )
FileType( 'T1 MRI to DW Diffusion MR Skeleton', 'T1 MRI to DW Diffusion MR Mask' )

FileType( 'Registered White Mesh', 'Mesh')
FileType( 'Registered Hemisphere Mesh', 'Mesh')
FileType( 'Left Registered White Mesh', 'Registered White Mesh')
FileType( 'Right Registered White Mesh', 'Registered White Mesh')
FileType( 'Left Registered Hemisphere Mesh', 'Registered Hemisphere Mesh')
FileType( 'Right Registered Hemisphere Mesh', 'Registered Hemisphere Mesh')

#fixme: might be a good idea to check the type of the mesh used in t1 space to be more pertinent
#fixme Meshes in Diffusion Space: Rem convenient because of non linear transform but could be better to have a converter implemented.

#----------------------Miscellaneous-----------------------------------------------------------------------------|
FileType( 'Tissue Partial Volume Estimation','3D Volume')
FileType( 'CSF Partial Volume Estimation', 'Tissue Partial Volume Estimation' )
FileType( 'GM Partial Volume Estimation', 'Tissue Partial Volume Estimation' )
FileType( 'WM Partial Volume Estimation', 'Tissue Partial Volume Estimation')


###########################################LOCAL MODELING TYPES AND FORMATS ############################################

Format('Numpy Array','f|*.npy')
Format('Compressed Numpy Array','f|*.npz')
FileType('Numpy Array','Any Type',['Numpy Array','Compressed Numpy Array'])

Format('Joblib Pickle file', 'f|*.pkl')
FileType('Joblib Pickle file', 'Any Type', 'Joblib Pickle file')

#-----------------------------------------Acquisition Scheme: B Vectors and Intensities----------------------|

#Fixme: these filetype only mirror bvecs and bvals in preprocessing part are they necessary? no, commented at the moment
#  suppress them later
FileType( 'Gradient Table', 'Joblib Pickle file' )

#-----------------------------------------Local Models Estimation and Prediction---------------------------------------|

FileType( 'Local Model', 'Joblib Pickle file' )
#Fixme: maybe there is a more convenient way to store the fit sing bucket or nifti? may use .minf file
FileType( 'Model Parameters', '4D Volume','gz compressed NIFTI-1 image')
FileType( 'Predicted Signal', '4D Volume','gz compressed NIFTI-1 image')
FileType( 'Residuals','4D Volume','gz compressed NIFTI-1 image')

#-----------------------------DTI-------------------------------------------------------|
FileType( 'Diffusion Tensor Model', 'Local Model' )# may be not necessary
FileType( 'Diffusion Tensor Coefficients', 'Model Parameters' )
FileType( 'DTI Predicted Signal', 'Predicted Signal' )
FileType( 'DTI Residuals','Residuals')

#-----------------------------Spherical Harmonic Based Model-----------------------------|
FileType( 'Spherical Harmonic Model', 'Local Model' )
#-----------------------------Constrained Spherical Deconvolution -----------------------|
FileType( 'Constrained Spherical Deconvolution Model', 'Spherical Harmonic Model' )
FileType( 'Single Fiber Response', 'Joblib Pickle file')
FileType( 'CSD Predicted Signal', 'Predicted Signal' )
FileType( 'CSD Residuals','Residuals')

#----------------------------------Scalar derived indices from Models(FA, MD..)----------|
#FIXME: indicate from which model is derived the quantity in type ?
FileType( 'Diffusion Scalar Map', '3D Volume')
FileType( 'Mean Diffusivity Volume', 'Diffusion Scalar Map')
FileType( 'Generalized Fractionnal Anisotropy Volume', 'Diffusion Scalar Map' )
    #Tensor derived quantities
FileType( 'Fractionnal Anisotropy Volume', 'Generalized Fractionnal Anisotropy Volume' )
FileType( 'Colored Fractionnal Anisotropy', '4D Volume','gz compressed NIFTI-1 image')
FileType( 'Apparent Diffusion Coefficient Volume', 'Diffusion Scalar Map' )
FileType( 'Eigen Vectors Volume', '4D Volume','gz compressed NIFTI-1 image')
FileType( 'First Eigen Vector Volume', '4D Volume','gz compressed NIFTI-1 image')
FileType( 'Second Eigen Vector Volume', '4D Volume','gz compressed NIFTI-1 image')
FileType( 'Third Eigen Vector Volume', '4D Volume','gz compressed NIFTI-1 image')
FileType( 'Eigen Values Volume', '4D Volume','gz compressed NIFTI-1 image')

#-----------------------Optional Tensor Based Derived Quantities-----------------------|
#Fixme: Use generic type Diffusion Scalar Map and requiredAttributes instead?
FileType( 'Axial Diffusivity Volume','Diffusion Scalar Map' )
FileType( 'Planarity Volume','Diffusion Scalar Map')
FileType( 'Sphericity Volume', 'Diffusion Scalar Map')
FileType( 'Linearity Volume', 'Diffusion Scalar Map')
FileType( 'Geodesic Diffusivity Volume', 'Diffusion Scalar Map')
FileType( 'Mode Volume', 'Diffusion Scalar Map')
    # EAP models derived quantities
FileType( 'RTOP Volume', 'Diffusion Scalar Map' )

#------------------------------------------ODF-------------------------------------------------------------------------|

FileType( 'Orientation Distribution Function','4D Volume','gz compressed NIFTI-1 image' )
FileType( 'Spherical Harmonics Coefficients','4D Volume','gz compressed NIFTI-1 image' )

# #----------------------------------------Meshes and Texture------------------------------------------------------------|

FileType('Sphere Template', 'Mesh')
FileType('Spherical Function Mesh', 'Mesh')
FileType('Spherical Function Texture', 'Texture')
#FileType('Mrtrix Sphere','Text File')
#FileType('ROI Texture','Texture')



############################################# TRACTOGRAPHY #############################################################

FileType('Seeds', 'Text File')
FileType('Raw Streamlines','Numpy Array')
#Streamlines bundle in trackvis file: in a near future nibabel will be able to handle it correctly
Format( 'Trackvis tracts', 'f|*.trk' )
FileType( 'Trackvis Streamlines','Any Type', 'Trackvis tracts' )
FileType('Global Streamlines', 'Trackvis Streamlines')
FileType('Streamlines Density Map', 'Diffusion MR Mask')



