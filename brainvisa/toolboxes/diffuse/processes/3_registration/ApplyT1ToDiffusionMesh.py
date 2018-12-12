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

def validation():
    from soma.wip.application.api import Application
    from distutils.spawn import find_executable
    configuration = Application().configuration
    fsl_prefix = configuration.FSL.fsl_commands_prefix
    cmds = ['fslsplit']
    for i, cmd in enumerate(cmds):
        executable = find_executable(fsl_prefix + cmd)
        if not executable:
            raise ValidationError('FSL command ' + cmd + ' could not be located on your system. Please check you FSL installation and/or fsldir , fsl_commands_prefix variables in BrainVISA preferences') 
    pass


from brainvisa.processes import *
from soma.wip.application.api import Application
from brainvisa.diffuse.tools import array_to_vol
from brainvisa.registration import getTransformationManager
from copy import copy
import numpy as np
import nibabel as nib


name = 'Apply T1 to Diffusion transform to Mesh'
userLevel = 0

signature=Signature(
    'b0_volume', ReadDiskItem( 'B0 Volume', 'gz compressed NIFTI-1 image' ),
    'T1_volume', ReadDiskItem( 'T1 MRI Bias Corrected', 'Aims readable volume formats' ),
    'side', Choice( "left", "right" ),
    'WM_mesh_in_T1', ReadDiskItem( 'Hemisphere White Mesh', 'Aims mesh formats' ),
    'GM_mesh_in_T1', ReadDiskItem( 'Hemisphere Mesh', 'Aims mesh formats' ),
    'T1_to_diff_linear_xfm', ReadDiskItem( 'Transform T1 MRI to Diffusion MR', 'Transformation matrix' ),
    'diff_to_T1_nonlinear_dfm', ReadDiskItem( 'NL Deform Diffusion MR to T1 MRI', 'Aims readable volume formats' ),
    #'registration_method', Choice("niftyreg", "fnirt"),
    
    'WM_mesh_in_DWI', WriteDiskItem('Registered White Mesh' , 'GIFTI file' ), #Registered White
    'GM_mesh_in_DWI', WriteDiskItem('Registered Hemisphere Mesh' , 'GIFTI file' ), #Registered White 
)

def meshTransform(mesh, deformation, voxel_size, affine2mm):
    vert = np.array(mesh.vertex())
    vert_new = np.empty_like(vert)
    for i, vertice in enumerate(vert):
        v_vx = vertice / voxel_size
        # Find the 8 voxel centers surrounding v
        A = np.floor(v_vx).astype(int)  # voxel lowest corner
        M = A + voxel_size / 2.0  # voxel (center) coordinates
        inferior = v_vx < M
        superior = v_vx > M
        N = M + (inferior * -1 + superior * 1) * voxel_size
        [x0, y0, z0] = np.min([M, N], 0)
        [x1, y1, z1] = np.max([M, N], 0)
        [X0, Y0, Z0] = np.floor([x0, y0, z0]).astype(int)
        [X1, Y1, Z1] = np.floor([x1, y1, z1]).astype(int)
        xd = (vertice[0] - x0) / max((x1 - x0),1e-10)
        yd = (vertice[1] - y0) / max((y1 - y0),1e-10)
        zd = (vertice[2] - z0) / max((z1 - z0),1e-10)
        c00 = deformation[X0, Y0, Z0] * (1 - xd) + deformation[X1, Y0, Z0] * xd
        c01 = deformation[X0, Y0, Z1] * (1 - xd) + deformation[X1, Y0, Z1] * xd
        c10 = deformation[X0, Y1, Z0] * (1 - xd) + deformation[X1, Y1, Z0] * xd
        c11 = deformation[X0, Y1, Z1] * (1 - xd) + deformation[X1, Y1, Z1] * xd
        c0 = c00 * (1 - yd) + c10 * yd
        c1 = c01 * (1 - yd) + c11 * yd
        c = c0 * (1 - zd) + c1 * zd
        vert_new[i] = np.linalg.inv(affine2mm)[:3,:3].dot(c)+np.linalg.inv(affine2mm)[:3,3]
    for i, v in enumerate(mesh.vertex()):
        v.assign(vert_new[i])
    return mesh

def meshSide( self, side ):
    signature = copy( self.signature )
    if side == 'left':
        signature['WM_mesh_in_T1'] = ReadDiskItem('Left Hemisphere White Mesh', 'Aims mesh formats')
    elif side == 'right':
        signature['WM_mesh_in_T1'] = ReadDiskItem('Right Hemisphere White Mesh', 'Aims mesh formats')
    signature['GM_mesh_in_T1'] = ReadDiskItem('Hemisphere Mesh', 'Aims mesh formats', requiredAttributes = {'side':self.side})
    signature['WM_mesh_in_DWI'] = WriteDiskItem('Registered White Mesh' , 'GIFTI file', requiredAttributes={'side':self.side})
    signature['GM_mesh_in_DWI'] = WriteDiskItem('Registered Hemisphere Mesh' , 'GIFTI file', requiredAttributes={'side':self.side})
    self.changeSignature( signature )

def initialization( self ):

    self.linkParameters( 'T1_to_diff_linear_xfm', 'b0_volume' )
    self.linkParameters('diff_to_T1_nonlinear_dfm', 'b0_volume')
    self.linkParameters( 'WM_mesh_in_T1', 'T1_volume' )
    self.linkParameters( 'GM_mesh_in_T1', 'WM_mesh_in_T1' )
    self.linkParameters('WM_mesh_in_DWI', 'b0_volume')
    self.linkParameters('GM_mesh_in_DWI', 'WM_mesh_in_DWI')
    self.addLink(None, 'side', self.meshSide)

def execution( self, context ):

    configuration = Application().configuration

    tmp_file = context.temporary('File')
    tmp_deform = context.temporary('File')

    #if self.registration_method == 'niftyreg':
        # new niftyreg deformation volume is X,Y,Z,1,3 instead of X,Y,Z,3
    deform_vol = nib.load(self.diff_to_T1_nonlinear_dfm.fullPath())
    if len(deform_vol.shape)==5:
        deform = deform_vol.get_data()
        deform = deform[...,0,:]
        nib.save(nib.Nifti1Image(deform,deform_vol.affine),tmp_deform.fullPath() + '.nii.gz')
    else:
        nib.save(deform_vol, tmp_deform.fullPath() + '.nii.gz')
    #reuse Lucile code to split volume cause dont want to mess with orientations as it worked
    cmd = [configuration.FSL.fsl_commands_prefix + 'fslsplit', tmp_deform.fullPath() + '.nii.gz' , tmp_file.fullPath(), '-t']
    context.system(*cmd)
    context.write(tmp_file.fullPath())
    f1 = aims.read(tmp_file.fullPath() + '0000.nii.gz')
    f2 = aims.read(tmp_file.fullPath() + '0001.nii.gz')
    f3 = aims.read(tmp_file.fullPath() + '0002.nii.gz')
    f = np.concatenate((f1.arraydata(), f2.arraydata(), f3.arraydata()))
    field = np.swapaxes(f, 0,3)
    field = np.swapaxes(field, 1,2)
    vxsize = np.array(f1.header()['voxel_size'][:3])
    affine = f1.header()['transformations']
    affine_mm = np.reshape(affine[0], (4, 4))

    mesh = aims.read(self.WM_mesh_in_T1.fullPath())
    new_mesh = meshTransform(mesh, field, vxsize, affine_mm)
    aims.write(new_mesh, self.WM_mesh_in_DWI.fullPath())
    cmd = [ 'AimsMeshTransform', '-i', self.WM_mesh_in_DWI, '-t', self.T1_to_diff_linear_xfm, '-o', self.WM_mesh_in_DWI ]
    context.system( *cmd )
    transformManager = getTransformationManager()
    transformManager.copyReferential( self.b0_volume, self.WM_mesh_in_DWI )

    mesh = aims.read(self.GM_mesh_in_T1.fullPath())
    new_mesh = meshTransform(mesh, field, vxsize, affine_mm)
    aims.write(new_mesh, self.GM_mesh_in_DWI.fullPath())
    cmd = [ 'AimsMeshTransform', '-i', self.GM_mesh_in_DWI, '-t', self.T1_to_diff_linear_xfm, '-o', self.GM_mesh_in_DWI ]
    context.system( *cmd )
    transformManager = getTransformationManager()
    transformManager.copyReferential( self.b0_volume, self.GM_mesh_in_DWI )

    # elif self.registration_method == 'fnirt':
    #     field_file = context.temporary('gz compressed NIFTI-1 image')
    #     # cmd = [configuration.FSL.fsl_commands_prefix + 'fnirtfileutils', '-i', self.diff_to_T1_nonlinear_dfm.fullPath(), '-r', self.T1_volume.fullPath(), '-o', field_file.fullPath()]
    #     # context.system(*cmd)
    #     cmd = [configuration.FSL.fsl_commands_prefix + 'fslsplit', self.diff_to_T1_nonlinear_dfm.fullPath(), tmp_file.fullPath(), '-t']
    #     context.system(*cmd)
    #     f1 = aims.read(tmp_file.fullPath() + '0000.nii.gz')
    #     f2 = aims.read(tmp_file.fullPath() + '0001.nii.gz')
    #     f3 = aims.read(tmp_file.fullPath() + '0002.nii.gz')
    #     f = np.concatenate((f1.arraydata(), f2.arraydata(), f3.arraydata()))
    #     field = np.swapaxes(f, 0, 3)
    #     field = np.swapaxes(field, 1, 2)
    #     t1 = aims.read(self.T1_volume.fullPath())
    #     vxsize = np.array(f1.header()['voxel_size'][:3])
    #     affine = t1.header()['transformations']
    #     # affine = f1.header()['transformations']
    #     affine_mm = np.reshape(affine[0], (4, 4))
    #
    #     mesh = aims.read(self.WM_mesh_in_T1.fullPath())
    #     new_mesh = meshTransform(mesh, field, vxsize, affine_mm)
    #     aims.write(new_mesh, self.WM_mesh_in_DWI.fullPath())
    #     transformManager = getTransformationManager()
    #     transformManager.copyReferential(self.b0_volume, self.WM_mesh_in_DWI)
    #
    #     mesh = aims.read(self.GM_mesh_in_T1.fullPath())
    #     new_mesh = meshTransform(mesh, field, vxsize, affine_mm)
    #     aims.write(new_mesh, self.GM_mesh_in_DWI.fullPath())
    #     transformManager = getTransformationManager()
    #     transformManager.copyReferential(self.b0_volume, self.GM_mesh_in_DWI)

    context.write('Finished')





