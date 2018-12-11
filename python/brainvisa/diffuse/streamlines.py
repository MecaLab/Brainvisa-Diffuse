"""


"""


import numpy as np
from soma import aims
import nibabel as nib
from dipy.tracking.metrics import frenet_serret
from brainvisa.diffuse.meshes import vertices_and_faces_to_mesh, mesh_2D_merge

##########################################################INPUT/OUTPUT###################################################################

def load_streamlines(path_file,lazy=True):
    """
    :param path_file: .tck or .trk . location of the file containing the streamlines
    :param lazy: boolean (True by default). lazy load of the tractogram. If false, the whole tractogram is loaded into memory.
    :return: tractogram , header
    """
    file = nib.streamlines.load(path_file,lazy_load=lazy)
    affine = file.affine
    tractogram = file.tractogram
    aims_vox_to_ras_mm = tractogram.affine_to_rasmm
    aims_vox_to_aims_mm = np.diag(header['voxel_sizes'].tolist() + [1])
    ras_mm_to_aims_mm = np.dot(aims_vox_to_aims_mm,np.linalg.inv(aims_vox_to_ras_mm))
    tractogram = tractogram.apply_affine(ras_mm_to_aims_mm, lazy=lazy)
    return tractogram, header

######################################################BUNDLE PROCESSING##################################################################

def cumulative_sizes(bundle):
    '''
    Useful function to index results coming from the bundle
    :param bundle:
    :return:
    '''
    sizes = np.array([len(s) for i, s in enumerate(bundle)])
    cumsizes = np.cumsum(sizes)
    return cumsizes


def compute_frenet_serret(bundle):
    '''Extend frenet Serret invariant function to whole bundle of streamlines
    This is the fastest but greedy version which require to keep in memory the whole bundle '''
    print len(bundle)
    cs = cumulative_sizes(bundle)
    nb_points = cs[-1]
    T = np.zeros((nb_points, 3))
    N = np.zeros((nb_points, 3))
    B = np.zeros((nb_points, 3))
    k = np.zeros((nb_points, 1))
    t = np.zeros(nb_points)
    for i, s in enumerate(bundle):
        T_, N_, B_, k_, t_ = frenet_serret(s)
        if i == 0:
            T[:cs[i]] = T_
            N[:cs[i]] = N_
            B[:cs[i]] = B_
            k[:cs[i]] = k_
            t[:cs[i]] = t_
        else:
            T[cs[i - 1]:cs[i]] = T_
            N[cs[i - 1]:cs[i]] = N_
            B[cs[i - 1]:cs[i]] = B_
            k[cs[i - 1]:cs[i]] = k_
            t[cs[i - 1]:cs[i]] = t_
    return T, N, B, k, t



######################################################CONVERSION#########################################################################

def build_2D_line(n):
    '''
    Build streamlines faces out of a set of n vertices assuming the mesh is a line without loop
    :param n: number of vertices (at least 2)
    :return: indices of mesh faces.
    '''
    faces = np.zeros((n-1,2), dtype=np.int16)
    faces[:, 0] = np.arange(n-1)
    faces[:,1] = np.arange(1, n)
    return faces


def vertices_to_2d_line(vertices):
    '''
    :param vertices: a Nx3 ndarray
    :return: mesh
    '''
    if len(vertices) == 0:
        mesh = aims.TimeSurface()
    else:
        faces = build_2D_line(vertices.shape[0])
        mesh = vertices_and_faces_to_mesh(vertices, faces)
    return mesh


def bundle_to_mesh(bundle, encode_local=False):
    '''
    :param streamline: streamlines coordinates
    :return: mesh
    '''
    if len(bundle) == 0:
        mesh = aims.TimeSurface()
    else:
        for i, s in enumerate(bundle):
            faces = build_2D_line(len(s))
            streamline = vertices_and_faces_to_mesh(s, faces)
            if i == 0:
                mesh = streamline
            else:
                mesh_2D_merge(mesh, streamline)
        if encode_local:
            T, N, B, k, t = compute_frenet_serret(bundle)
            del N,B,k,t
            set_local_orientation(mesh,T)
    return mesh


def set_local_orientation(mesh, local_orientation):
    '''Add local information orientation at vertex level (or streamline level)
    to be used in Anatomist for coloring the streamlines.
    :param mesh : AimsTimeSurface containing n vertices
    :param local_orientation : a Nx3 array containing local orientation infornation (e.g normal or tangent)
    '''
    #normalizing data using default 2-norm
    #norm = np.linalg.norm(local_orientation,axis=1)
    #build our own norm function
    norm = np.sqrt(np.sum(local_orientation**2,axis=1))
    #depending on the version of numpy it might not be accurate to use this function
    local_orientation[norm!=0]/=norm[norm!=0][:,np.newaxis]
    mesh.normal().assign([aims.AimsVector(x, dtype='FLOAT', dim=3) for x in local_orientation])
    pass





