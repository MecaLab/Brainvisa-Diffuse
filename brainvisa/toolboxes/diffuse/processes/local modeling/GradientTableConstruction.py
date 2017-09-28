


from brainvisa.processes import *
from soma import aims
import numpy as np
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
from joblib import dump



userLevel = 0

name = 'Gradient Table Construction'
category = 'import'

signature = Signature(
    'diffusion_data', ReadDiskItem(
        'Corrected DW Diffusion MR',
        'gz compressed NIFTI-1 image'
    ),
    'bvecs', ReadDiskItem(
        'Corrected B Vectors',
        'Text file'
    ),
    'bvals', ReadDiskItem(
        'Raw B Values', 'Text file'
    ),
    'round_bvals', Boolean(),
    'b0_threshold', Float(),

    'gradient_table', WriteDiskItem(
        'Gradient Table',
        'Joblib Pickle file'
    ),

)


def initialization( self ):
    self.addLink('bvecs', 'diffusion_data')
    self.addLink('bvals','bvecs' )
    self.addLink('gradient_table', 'bvecs' )
    self.b0_threshold = 50




def execution( self, context):
    bvals, bvecs = read_bvals_bvecs(self.bvals.fullPath(), self.bvecs.fullPath())
    if self.round_bvals:
        context.write("Rouding bvalues: useful for shell based models")
        bvals = np.round(bvals,-2)
    try:
        minf = self.diffusion_data.minf()
        t = minf['storage_to_memory']
    except KeyError:
        context.write("No storage_to_memory field in the  minf file associated to the volume, using the one of the header of the volume")
        dwi = aims.read(self.diffusion_data.fullPath())
        header = dwi.header()
        t = header['storage_to_memory']
    finally:
        try :
            t1 = aims.AffineTransformation3d(t).toMatrix()
            aff = np.diag(t1)[:-1]
            affine = np.diag(aff)
        except:
            context.write("Warning!: there is no storage to memory matrix, I assume bvecs have an RAS (Nifti convention) orientation")
            affine = -1.0*np.eye(3)

    context.write("The following transformation is going to be applied:", affine)
    bvecs = np.dot(bvecs, np.transpose(affine))
    context.write("Transforming bvecs coordinate from storage to Aims referential")


    gtab = gradient_table(bvals, bvecs,b0_threshold=self.b0_threshold)
    dump(gtab, self.gradient_table.fullPath(), compress=9)

    #Handling metadata
    self.gradient_table.setMinf('rounded_bvals', self.round_bvals)
    self.gradient_table.setMinf('bvalues_uuid', self.bvals.uuid())
    self.gradient_table.setMinf('bvectors_uuid',self.bvecs.uuid())




