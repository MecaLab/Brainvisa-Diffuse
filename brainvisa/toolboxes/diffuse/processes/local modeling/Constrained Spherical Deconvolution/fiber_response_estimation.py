
from brainvisa.processes import *


userLevel = 0

name = 'Single Fiber Response Estimation'
category = 'Local_modeling'

signature = Signature(
    'diffusion_data', ReadDiskItem(
        'Corrected DW Diffusion MR',
        'Aims readable volume formats'
    ),
    'mask', ReadDiskItem(
        'Diffusion MR Mask',
        'Aims readable volume formats'
    ),
    'response', WriteDiskItem(
        'Single Fiber Response',
        'Joblib Pickle File'
    ),
)




def initialization ( self ):

    eNode = SelectionExecutionNode(self.name, parameterized=self)
    eNode.addChild('Recursive',
                   ProcessExecutionNode('Recursive Estimation', optional=True, selected=True))
    eNode.addChild('FromDTI',
                   ProcessExecutionNode('DTI Estimation', optional=True, selected=False))
    eNode.addChild('Default',
                   ProcessExecutionNode('Default Prolate Response', optional=True,selected=False))


    #Linking
    # self.addLink(['mask','sphere'],None,self.switch_pipeline_signature)
    self.addLink('mask','diffusion_data')
    self.addLink('response','diffusion_data')
    #Default
    eNode.removeLink('Default.response','Default.diffusion_data')
    eNode.addLink('Default.diffusion_data','diffusion_data')
    eNode.addLink('Default.response','response')
    #DTI
    #eNode.FromDTI.setOptional('mask')
    eNode.removeLink('FromDTI.response', 'FromDTI.diffusion_data')
    eNode.removeLink('FromDTI.mask', 'FromDTI.diffusion_data')
    eNode.addLink('FromDTI.diffusion_data', 'diffusion_data')
    eNode.addLink('FromDTI.response', 'response')
    eNode.addLink('FromDTI.mask', 'mask')
    #Recursive
    eNode.removeLink('Recursive.response', 'Recursive.diffusion_data')
    eNode.removeLink('Recursive.mask', 'Recursive.diffusion_data')
    eNode.addLink('Recursive.diffusion_data', 'diffusion_data')
    eNode.addLink('Recursive.response', 'response')
    eNode.addLink('Recursive.mask','mask')


    self.setOptional('mask')
    #self.setOptional('sphere')




    self.setExecutionNode(eNode)
    pass













