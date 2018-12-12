
from brainvisa.processes import *


userLevel = 0
name = '3. Local Tractography Pipeline'


signature = Signature(

    'sh_coefficients', ReadDiskItem(
        'Spherical Harmonics Coefficients',
        'gz compressed NIFTI-1 image'
    ),
    'type', Choice('DETERMINISTIC','PROBABILISTIC'),
    'tracking_algorithm', Choice(('Default','DEF'),('Particle Filtering','PFT')),
    'seeding_mask', ReadDiskItem(
        'Diffusion MR Mask',
		'Aims readable volume formats'
    ),
    'seeding_mesh', ReadDiskItem(
        'Registered White Mesh',
		'GIFTI file'
    ),
    'surfacic_roi', ReadDiskItem(
         'ROI Texture',
        'GIFTI file'
    ),
    'tracking_quality',Choice('High','Medium','Coarse'),

    'seeds', WriteDiskItem(
        'Seeds',
        'Text File'
    ),
    'streamlines', WriteDiskItem(
		'Streamlines',
		'Trackvis tracts'
	),
)
#sum up of the available configurations
tracking_configurations = [{'type':'DETERMINISTIC','tracking_quality':'High','max_ang':30,'step':0.1},
                           {'type': 'DETERMINISTIC', 'tracking_quality': 'Medium', 'max_ang': 30, 'step': 0.5},
                           {'type': 'DETERMINISTIC', 'tracking_quality': 'Coarse', 'max_ang': 30, 'step': 1},
                           {'type': 'PROBABILISTIC', 'tracking_quality': 'High', 'max_ang': 45, 'step': 0.1,'nb_samp':500},
                           {'type': 'PROBABILISTIC', 'tracking_quality': 'Medium', 'max_ang': 45, 'step': 0.5,'nb_samp':50},
                           {'type': 'PROBABILISTIC', 'tracking_quality': 'Coarse', 'max_ang': 45, 'step': 1,'nb_samp':1},
                           ]


def set_tracking_configuration(self, dumb,dumb1):

    eNode = self.executionNode()
    if self.tracking_quality == 'High' and self.type == 'DETERMINISTIC':
        eNode.Tracking.Default.max_angle = 30
        eNode.Tracking.Default.step_size = 0.1
        eNode.Tracking.Default.nb_sample = 1

        eNode.Tracking.PFT.max_angle = 30
        eNode.Tracking.PFT.step_size = 0.1
        eNode.Tracking.PFT.nb_sample = 1

    elif self.tracking_quality == 'High' and self.type == 'PROBABILISTIC':
        eNode.Tracking.Default.max_angle = 45
        eNode.Tracking.Default.step_size = 0.1
        eNode.Tracking.Default.nb_sample = 500

        eNode.Tracking.PFT.max_angle = 45
        eNode.Tracking.PFT.step_size = 0.1
        eNode.Tracking.PFT.nb_sample = 500

    elif self.tracking_quality == 'Medium' and self.type == 'DETERMINISTIC':

        eNode.Tracking.Default.max_angle = 30
        eNode.Tracking.step_size = 0.5
        eNode.Tracking.nb_sample = 1
        eNode.Tracking.PFT.max_angle = 30
        eNode.Tracking.PFT.step_size = 0.5
        eNode.Tracking.PFT.nb_sample = 1

    elif self.tracking_quality == 'Coarse' and self.type == 'DETERMINISTIC':
        eNode.Tracking.Default.max_angle = 30
        eNode.Tracking.Default.step_size = 1
        eNode.Tracking.Default.nb_sample = 1

        eNode.Tracking.PFT.max_angle = 30
        eNode.Tracking.PFT.step_size = 1
        eNode.Tracking.PFT.nb_sample = 1

    elif self.tracking_quality == 'Medium' and self.type == 'PROBABILISTIC':
        eNode.Tracking.Default.max_angle = 45
        eNode.Tracking.Default.step_size = 0.5
        eNode.Tracking.Default.nb_sample = 30

        eNode.Tracking.PFT.max_angle = 45
        eNode.Tracking.PFT.step_size = 0.5
        eNode.Tracking.PFT.nb_sample = 30

    elif self.tracking_quality == 'Coarse' and self.type == 'PROBABILISTIC':
        eNode.Tracking.Default.max_angle = 45
        eNode.Tracking.Default.step_size = 1
        eNode.Tracking.Default.nb_sample = 1

        eNode.Tracking.PFT.max_angle = 45
        eNode.Tracking.PFT.step_size = 1
        eNode.Tracking.PFT.nb_sample = 1
    pass


#removed other constraint strategies to use the Anatomical Constraint (more accurate)
# def switching_classifier(self,dumb):
#     signature = copy(self.signature)
#     if self.constraint == 'Binary':
#         self.setHidden('scalar_volume','include_pve_map','exclude_pve_map','threshold')
#         self.setOptional('scalar_volume','include_pve_map','exclude_pve_map','threshold')
#         self.setEnable('mask')
#     elif self.constraint == 'Threshold':
#         self.setHidden('mask', 'include_pve_map', 'exclude_pve_map')
#         self.setEnable('scalar_volume','threshold')
#     elif self.constraint == 'Anatomical':
#         self.setHidden('scalar_volume', 'mask' , 'threshold')
#         self.setEnable('include_pve_map','exclude_pve_map')
#         self.setOptional('mask')
#     self.changeSignature(signature)


# def switching_seeding_strategy(self,dumb):
#     signature = copy(self.signature)
#     eNode = self.getExecutionNode()
#     if eNode.Seeding.SeedsFromMesh.isSelected():
#         self.setHidden('seeding_mesh')
#         self.setOptional('seeding_mesh')
#         self.setEnable('seeding_mask')
#     else:
#         self.setHidden('seeding_mask')
#         self.setOptional('seeding_mask')
#         self.setEnable('seeding_mesh')
#     self.changeSignature(signature)




def initialization(self):

    #Pipeline GRAPH
    eNode = SerialExecutionNode( self.name, parameterized=self )

    eNode.addChild('Seeding',
                   ProcessExecutionNode('seeding_pipeline',optional=True))

    trackingNode = SelectionExecutionNode('Tracking Algorithm', optional=False, selected=1, expandedInGui=1)
    trackingNode.addChild('Default',
                          ProcessExecutionNode('usual_local_tracking', optional=True, selected=True)
                          )
    trackingNode.addChild('PFT',
                          ProcessExecutionNode('particle_filtering_tracking', optional=True, selected=False)
                          )
    eNode.addChild('Tracking', trackingNode)


    self.setExecutionNode(eNode)


    def switchTracking(enabled, names, parameterized):
        eNode = parameterized[0].executionNode()
        if self.tracking_algorithm == 'DEF':
            eNode.Tracking.Default.setSelected(True)
        elif self.tracking_algorithm == 'PFT':
            eNode.Tracking.PFT.setSelected(True)
        pass



    ##Seeding Nodes

    eNode.Seeding.VolumicSeeds.removeLink('seeds', 'mask')
    eNode.Seeding.VolumicSeeds.removeLink('seeds', 'mask')

    self.addLink('Seeding.VolumicSeeds.mask','seeding_mask')
    self.addLink('Seeding.RVolumicSeeds.mask','seeding_mask')

    self.addLink('Seeding.VolumicSeeds.seeds', 'seeds')
    self.addLink('Seeding.RVolumicSeeds.seeds', 'seeds')


    #Tracking Nodes
    eNode.Tracking.Default.removeLink('seeds', 'sh_coefficients')
    eNode.Tracking.PFT.removeLink('seeds', 'sh_coefficients')

    eNode.Tracking.Default.removeLink('streamlines', 'sh_coefficients')
    eNode.Tracking.PFT.removeLink('streamlines', 'sh_coefficients')

    #Linking main to tracking : should be identical params
    ###########################################################

    eNode.addLink('Tracking.Default.sh_coefficients', 'sh_coefficients')
    eNode.addDoubleLink('Tracking.Default.type', 'type')
    eNode.addLink('Tracking.Default.seeds', 'seeds')
    eNode.addLink('Tracking.Default.streamlines', 'streamlines')

    eNode.addLink('Tracking.PFT.sh_coefficients', 'sh_coefficients')
    eNode.addDoubleLink('Tracking.PFT.type', 'type')
    eNode.addLink('Tracking.PFT.seeds', 'seeds')
    eNode.addLink('Tracking.PFT.streamlines', 'streamlines')


    #Linking main:
    ############################################################
    self.addLink('seeding_mask', 'sh_coefficients')
    self.addLink('seeding_mesh','sh_coefficients')
    self.addLink('seeds', 'sh_coefficients')

   # self.addLink(None,None,self.switching_seeding_strategy)
    self.addLink(None,['tracking_quality','type'],self.set_tracking_configuration)
    self.addLink(None,'tracking_algorithm', switchTracking)
    self.addLink('streamlines', 'sh_coefficients')

    #default values
    self.type = 'DETERMINISTIC'
    self.tracking_quality = 'Medium'
    #remove
    self.setOptional('seeding_mask', 'seeding_mesh', 'surfacic_roi')
    self.setHidden('seeding_mesh','surfacic_roi')
    #Fix constraint tractography method
    eNode.Tracking.PFT.constraint = 'ACT'
    eNode.Tracking.Default.constraint = 'ACT'

    eNode.Tracking.PFT.setHidden('constraint')
    eNode.Tracking.Default.setHidden('constraint')







