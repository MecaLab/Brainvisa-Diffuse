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
from soma.wip.application.api import Application
from distutils.spawn import find_executable
from brainvisa.diffuse import BvecTransformation
from brainvisa.diffuse.variables import FSL_BAD_CONFIG_MSG, FSL_NO_FSLDIR
from brainvisa.registration import getTransformationManager
import numpy

name = 'Motion and Eddy-current correction (ECCAR)'
userLevel = 0

signature=Signature(
  'dwi_data', ReadDiskItem( 'Raw Denoised Diffusion MR', 'Aims readable volume formats' ),
  'bvals', ReadDiskItem( 'Raw B Values', 'Text file' ),
  'bvecs', ReadDiskItem( 'Reoriented B Vectors', 'Text file' ),
  'dwi_eddy_corrected', WriteDiskItem( 'EC corrected DW Diffusion MR', 'gz compressed NIFTI-1 image' ),
  'corrected_bvecs', WriteDiskItem( 'Corrected B Vectors', 'Text file' ),
)

def linkOutput(self, proc, dummy):
    required = {}
    required['center'] = self.dwi_data.get('center')
    required['subject'] = self.dwi_data.get('subject')
    required['acquisition'] = self.dwi_data.get('acquisition')
    return self.signature['dwi_unwarped'].findValue(self.dwi_data, requiredAttributes=required)

def initialization( self ):
    self.linkParameters( 'bvals', 'dwi_data' )
    self.linkParameters( 'bvecs', 'dwi_data' )
    self.linkParameters('dwi_eddy_corrected', 'dwi_data', self.linkOutput)
    self.linkParameters( 'corrected_bvecs', 'dwi_eddy_corrected' )

def execution( self, context ):

    context.write('Eddy-current distortion correction')


    configuration = Application().configuration

    #check that commands are correctly installed
    cmds = ['fslroi','flirt','convert_xfm']

    executables = [find_executable(c) for c in fsl_cmds]


        context.write('- Identification of first b0 volume')
        b0_tmp = context.temporary( 'gz compressed NIFTI-1 image' )
        bvals = numpy.loadtxt(self.bvals.fullPath())
        b0_index = numpy.where(bvals < 100)[0] ## bvals==0 not possible when bvalues take values +-5 or +-10
        cmd = [ configuration.FSL.fsl_commands_prefix + 'fslroi', self.dwi_data.fullPath(), b0_tmp.fullPath(), str(b0_index[0]), '1' ]
        context.system( *cmd )

        Nvol = self.dwi_data.get( 'volume_dimension', search_header=True )[3]
        img = aims.read(self.dwi_data.fullPath())
        data = img.arraydata()

        refvol = context.temporary( 'gz compressed NIFTI-1 image' )
        invol = context.temporary( 'gz compressed NIFTI-1 image' )
        outvol = context.temporary( 'gz compressed NIFTI-1 image' )
        b0mat = context.temporary( 'Text file' )
        omat = context.temporary( 'Text file' )

        context.write('- Affine registration of dwi volumes to b0 volumes... [~' + str(round(Nvol*0.5)) + 'min]')
        cmd = [ configuration.FSL.fsl_commands_prefix + 'fslroi', self.dwi_data.fullPath(), refvol.fullPath(), '0', '1' ]
        context.system( *cmd )
        corrected_volume = numpy.zeros_like(data[:, :, :, :])
        directory = os.path.dirname(self.dwi_eddy_corrected.fullPath())
        log_file = os.path.splitext(os.path.splitext(self.dwi_eddy_corrected.fullPath())[0])[0]+ '.ecclog'
        f = open(log_file, 'w')
        for ind in range(Nvol):
            context.write(ind)
            if ind in b0_index:
                cmd = [ configuration.FSL.fsl_commands_prefix + 'fslroi', self.dwi_data.fullPath(), refvol.fullPath(), str(ind), '1' ]
                context.system( *cmd )
                cmd = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-interp', 'spline', '-cost', 'mutualinfo', '-in', refvol.fullPath(), '-ref', b0_tmp.fullPath(), '-omat', b0mat.fullPath(), '-dof', '12', '-out', outvol.fullPath() ]
                context.system( *cmd )
                mat = open(b0mat.fullPath(), 'r')
            else:
                cmd = [ configuration.FSL.fsl_commands_prefix + 'fslroi', self.dwi_data.fullPath(), invol.fullPath(), str(ind), '1' ]
                context.system( *cmd )
                cmd = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-interp', 'spline', '-cost', 'mutualinfo', '-in', invol.fullPath(), '-ref', refvol.fullPath(), '-omat', omat.fullPath(), '-dof', '12' ]
                context.system( *cmd )
                cmd = [ configuration.FSL.fsl_commands_prefix + 'convert_xfm', '-omat', omat.fullPath(), '-concat', omat.fullPath(), b0mat.fullPath() ]
                context.system( *cmd )
                cmd = [ configuration.FSL.fsl_commands_prefix + 'flirt', '-interp', 'spline', '-cost', 'mutualinfo', '-in', invol.fullPath(), '-ref', b0_tmp.fullPath(), '-applyxfm', '-init', omat.fullPath(), '-out', outvol.fullPath() ]
                context.system( *cmd )
                mat = open(omat.fullPath(), 'r')
            tmp_file = ''.join(['processing ', directory, '/EC_correction_tmp{0:03d}\n'.format(ind)])
            f.write(tmp_file)
            f.write('\nFinal result:\n')
            [f.write(line) for line in mat]
            f.write('\n')
            tmp_img = aims.read(outvol.fullPath())
            tmp_data = tmp_img.arraydata()
            corrected_volume[ind,:,:,:] = tmp_data
            mat.close()
        f.close()
        img = aims.read(self.dwi_data.fullPath())
        vol = aims.Volume(corrected_volume)
        vol.copyHeaderFrom(img.header())
        aims.write(vol, self.dwi_eddy_corrected.fullPath())
        transformManager = getTransformationManager()
        transformManager.copyReferential( self.dwi_data, self.dwi_eddy_corrected )

        context.write('- Bvecs rotation')
        BvecTransformation.bvecRotation(self.dwi_eddy_corrected.fullPath(), self.bvecs.fullPath(), self.corrected_bvecs.fullPath())

        context.write('Finished')
