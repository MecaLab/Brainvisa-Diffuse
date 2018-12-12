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

name = 'Denoising Pipeline'
userLevel = 0

signature = Signature(
    'dwi_data', ReadDiskItem('Raw Diffusion MR', 'Aims readable volume formats'),
    'coil_number', Integer(),
    'brain_mask', ReadDiskItem('T1 MRI to DW Diffusion MR Brain', 'Aims readable volume formats'),
    'denoised_dwi_data', WriteDiskItem('Denoised Diffusion MR', 'gz compressed NIFTI-1 image'),
)

def initialization(self):



    eNode = SerialExecutionNode( self.name, parameterized=self )

    eNode.addChild('Piesno',
                   ProcessExecutionNode('Piesno', optional=False))
    eNode.addChild('Selection',
                   SelectionExecutionNode('Denoising Algorithm', optional=False))
    eNode.Selection.addChild('LPCA',
                   ProcessExecutionNode('LPCA', selected=True))
    eNode.Selection.addChild('NLMS',
                   ProcessExecutionNode('NLMS', selected=False))

    # processing links
    #Pipeline Links
    self.addLink('denoised_dwi_data', 'dwi_data')
    self.addLink('brain_mask','dwi_data')
    self.addLink('denoised_dwi_data','dwi_data')

    #Piesno Links
    eNode.Piesno.removeLink('sigma','dwi_data')
    eNode.addLink('Piesno.dwi_data','dwi_data')
    eNode.addLink('Piesno.sigma', 'dwi_data')
    eNode.addDoubleLink('Piesno.coil_number','coil_number')

    #LPCA links
    eNode.Selection.LPCA.removeLink('sigma','dwi_data')
    eNode.Selection.LPCA.removeLink('brain_mask','dwi_data')
    eNode.Selection.LPCA.removeLink('denoised_dwi_data','dwi_data')

    eNode.addLink('Selection.LPCA.dwi_data','dwi_data')
    eNode.addLink('Selection.LPCA.brain_mask','brain_mask')
    eNode.addLink('Selection.LPCA.sigma', 'Piesno.sigma')
    eNode.addLink('Selection.LPCA.denoised_dwi_data','denoised_dwi_data')

    #NLMS links
    eNode.Selection.NLMS.removeLink('sigma', 'dwi_data')
    eNode.Selection.NLMS.removeLink('brain_mask', 'dwi_data')
    eNode.Selection.NLMS.removeLink('denoised_dwi_data', 'dwi_data')

    eNode.addLink('Selection.NLMS.dwi_data', 'dwi_data')
    eNode.addLink('Selection.NLMS.brain_mask', 'brain_mask')
    eNode.addLink('Selection.NLMS.sigma', 'Piesno.sigma')
    eNode.addLink('Selection.NLMS.denoised_dwi_data', 'denoised_dwi_data')

    self.setOptional('brain_mask')

    self.setExecutionNode(eNode)









