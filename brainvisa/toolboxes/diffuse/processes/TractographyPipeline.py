#
# from brainvisa.processes import *
# #from copy import copy
#
#
#
# userLevel = 2
# name = 'Local Tractography Pipeline'
#
#
# signature = Signature(
#
#     'sh_coefficients', ReadDiskItem(
#         'Spherical Harmonics Coefficients',
#         'gz compressed NIFTI-1 image'
#     ),
#     'type',Choice('DETERMINISTIC','PROBABILISTIC'),
#
#     'seeding_mask', ReadDiskItem(
#         'Diffusion MR Mask',
# 		'Aims readable volume formats'
#     ),
#
#     'seeding_mesh', ReadDiskItem(
#         'Registered White Mesh',
# 		'GIFTI file'
#     ),
#
#     'constraint', Choice('Binary','Threshold','Anatomical'),
#
#     'mask', ReadDiskItem(
#         'Diffusion MR Mask',
#         'gz compressed NIFTI-1 image'
#     ),
#     'scalar_volume', ReadDiskItem(
#         'Fractionnal Anisotropy Volume',
#         'gz compressed NIFTI-1 image'
#     ),
#     'include_pve_map', ReadDiskItem(
#         'Diffusion MR Mask',
#         'gz compressed NIFTI-1 image'
#     ),
#     'exclude_pve_map',ReadDiskItem(
#         'Diffusion MR Mask',
#         'gz compressed NIFTI-1 image'
#     ),
#     'threshold',Float(),
#
#     'tracking_quality',Choice('High','Medium','Coarse'),
#
#     'seeds', WriteDiskItem(
#         'Seeds',
#         'Text File'
#     ),
#     'streamlines', WriteDiskItem(
# 		'Raw Streamlines',
# 		'Numpy Array'
# 	),
#
# )
#
# tracking_configurations = [{'type':'DETERMINISTIC','tracking_quality':'High','max_ang':30,'step':0.1},
#                            {'type': 'DETERMINISTIC', 'tracking_quality': 'Medium', 'max_ang': 30, 'step': 0.5},
#                            {'type': 'DETERMINISTIC', 'tracking_quality': 'Coarse', 'max_ang': 30, 'step': 1},
#                            {'type': 'PROBABILISTIC', 'tracking_quality': 'High', 'max_ang': 45, 'step': 0.1,'nb_samp':500},
#                            {'type': 'PROBABILISTIC', 'tracking_quality': 'Medium', 'max_ang': 45, 'step': 0.5,'nb_samp':30},
#                            {'type': 'PROBABILISTIC', 'tracking_quality': 'Coarse', 'max_ang': 45, 'step': 1,'nb_samp':1},
#                            ]
#
#
# def set_tracking_configuration(self, dumb,dumb1):
#
#     eNode = self.executionNode()
#     if self.tracking_quality=='High' and self.type=='DETERMINISTIC':
#         eNode.Tracking.max_angle = 30
#         eNode.Tracking.step_size = 0.1
#         eNode.Tracking.nb_sample = 1
#     elif self.tracking_quality=='High' and self.type=='PROBABILISTIC':
#         eNode.Tracking.max_angle = 45
#         eNode.Tracking.step_size = 0.1
#         eNode.Tracking.nb_sample = 500
#     elif self.tracking_quality=='Medium' and self.type=='DETERMINISTIC':
#         eNode.Tracking.max_angle = 30
#         eNode.Tracking.step_size = 0.5
#         eNode.Tracking.nb_sample = 1
#     elif self.tracking_quality=='Coarse' and self.type=='DETERMINISTIC':
#         eNode.Tracking.max_angle = 30
#         eNode.Tracking.step_size = 1
#         eNode.Tracking.nb_sample = 1
#     elif self.tracking_quality=='Medium' and self.type=='PROBABILISTIC':
#         eNode.Tracking.max_angle = 45
#         eNode.Tracking.step_size = 0.5
#         eNode.Tracking.nb_sample = 30
#     elif self.tracking_quality=='Coarse' and self.type=='PROBABILISTIC':
#         eNode.Tracking.max_angle = 45
#         eNode.Tracking.step_size = 1
#         eNode.Tracking.nb_sample = 1
#
#
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
#
#
# # def switching_seeding_strategy(self,dumb):
# #     signature = copy(self.signature)
# #     eNode = self.getExecutionNode()
# #     if eNode.Seeding.SeedsFromMesh.isSelected():
# #         self.setHidden('seeding_mesh')
# #         self.setOptional('seeding_mesh')
# #         self.setEnable('seeding_mask')
# #     else:
# #         self.setHidden('seeding_mask')
# #         self.setOptional('seeding_mask')
# #         self.setEnable('seeding_mesh')
# #     self.changeSignature(signature)
#
#
#
#
# def initialization(self):
#
#     #Pipeline GRAPH
#     eNode = SerialExecutionNode( self.name, parameterized=self )
#
#     eNode.addChild('Seeding',
#                    ProcessExecutionNode('seeding_pipeline',optional=True))
#
#     eNode.addChild('Tracking',
#                    ProcessExecutionNode('tractography', optional=False))
#
#     self.setExecutionNode(eNode)
#
#
#     #Linkings:
#
#     #removing existing Links in Tracking process:
#     eNode.Tracking.removeLink('mask', 'sh_coefficients')
#     eNode.Tracking.removeLink('scalar_volume', 'sh_coefficients')
#     eNode.Tracking.removeLink('seeds', 'sh_coefficients')
#     eNode.Tracking.removeLink('streamlines', 'sh_coefficients')
#
#
#     #Linking main to tracking : should be identical params
#     ###########################################################
#
#     eNode.addLink('Tracking.sh_coefficients','sh_coefficients')
#     eNode.addLink('Tracking.type','type')
#     eNode.addLink('Tracking.constraint','constraint')
#     eNode.addLink('Tracking.mask','mask')
#     eNode.addLink('Tracking.scalar_volume','scalar_volume')
#     eNode.addLink('Tracking.threshold','threshold')
#     eNode.addLink('Tracking.include_pve_map','include_pve_map')
#     eNode.addLink('Tracking.exclude_pve_map','exclude_pve_map')
#     eNode.addLink('Tracking.seeds','seeds')
#     eNode.addLink('Tracking.streamlines','streamlines')
#
#     #removing existing overrided links in Seeding sub-pipelines
#     eNode.Seeding.SeedsFromMesh.removeLink('seeds','white_mesh')
#
#     #Linking main to seeding :
#     ############################################################
#     eNode.addLink('Seeding.SeedsFromMesh.white_mesh','seeding_mesh')
#     eNode.addLink('Seeding.SeedsFromMesh.seeds','seeds')
#     eNode.addLink('Seeding.RVolumicSeeds.mask','seeding_mask')
#     eNode.addLink('Seeding.VolumicSeeds.mask', 'seeding_mask')
#     eNode.addLink('Seeding.RVolumicSeeds.seeds', 'seeds')
#     eNode.addLink('Seeding.VolumicSeeds.seeds', 'seeds')
#
#     #Linking main:
#     ############################################################
#     self.addLink('seeding_mask', 'sh_coefficients')
#     self.addLink('mask', 'sh_coefficients')
#     self.addLink('seeding_mesh','sh_coefficients')
#     self.addLink('scalar_volume', 'sh_coefficients')
#     self.addLink('seeds', 'sh_coefficients')
#     self.addLink(None, 'constraint', self.switching_classifier)
#    # self.addLink(None,None,self.switching_seeding_strategy)
#     self.addLink(None,['tracking_quality','type'],self.set_tracking_configuration)
#     self.addLink('streamlines', 'sh_coefficients')
#
#     self.type='DETERMINISTIC'
#
#
#
#
#
#
