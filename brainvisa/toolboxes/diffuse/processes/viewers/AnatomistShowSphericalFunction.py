from brainvisa.processes import *
from brainvisa import anatomist

name = 'Anatomist Show Spherical Function'
userLevel = 0
roles = ('viewer',)


def validation():
	anatomist.validation()


signature = Signature(
	'spherical_function_texture', ReadDiskItem('Spherical Function Texture', 'GIFTI file'),
	'spherical_function_mesh', ReadDiskItem('Spherical Function Mesh', 'GIFTI file'),
)

def initialization(self):
	self.addLink('spherical_function_mesh', 'spherical_function_texture')


def execution(self, context):

	a = anatomist.Anatomist()
	text = a.loadObject(self.spherical_function_texture)
	mesh = a.loadObject(self.spherical_function_mesh)

	w = a.createWindow("3D")
	fusionTexture = a.fusionObjects([mesh, text], "FusionTexSurfMethod")
	w.addObjects(fusionTexture)

	return [w, fusionTexture]





































