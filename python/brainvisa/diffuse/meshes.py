"""
Mesh Handling Module:

Regroups Aims Meshes Input/Output (I/O) , Meshes
*
*
*

"""

from soma import aims
from copy import copy


def mesh_2D_merge(mesh_base, added_mesh):
    '''
    Merge 2d-meshes (Aims.SurfaceManip.meshMerge only handle 3D-meshes)
    The mesh_base parameter will be overwritten by the fusion (same behavior as in SurfaceManip.meshMerge)
    :param mesh_base: AimsTimeSurface_2D_VOID
    :param added_mesh: AimsTimeSurface_2D_VOID
    :return void
    '''
    # Fixing sizes of the respective mesh
    #copies are mandatory due to prevent from update on the fly of objects
    s1 = copy(mesh_base.vertex().size())
    s2 = copy(added_mesh.vertex().size())
    p1 = copy(mesh_base.polygon().size())
    p2 = copy(added_mesh.polygon().size())
    # Vertices fusion
    # Allocating space for fusion
    mesh_base.vertex().resize(s1 + s2)
    mesh_base.vertex()[s1:] = added_mesh.vertex()[:]
    # Polygons fusion
    # Allocating space for fusion
    mesh_base.polygon().resize(p1 + p2)
    # Due to weird comportment of polygons need to be done with for loop
    for i, p in enumerate(added_mesh.polygon()):
        p = p + s1
        mesh_base.polygon()[p1 + i] = p
    pass


def vertices_and_faces_to_mesh(vertices, faces, header=None):
    '''
    Create an aims 2D or 3D mesh using precomputed vertices and faces. Vertices and faces are assumed to be compatible
    :param vertices: ndarray (N,d)
    :param faces: ndarray (N1,d1)
    :param header: a dictionnary like structure
    :return: AimsTimeSurface
    '''
    # determine the mesh type based on polygon type (does not work for quads polygon !)
    poly_type = faces.shape[-1]
    mesh = aims.TimeSurface(dim=poly_type)
    v = mesh.vertex()
    p = mesh.polygon()

    v.assign([aims.Point3df(x) for x in vertices])
    p.assign([aims.AimsVector(x, dtype='U32', dim=poly_type) for x in faces])
    # recompute normals, not mandatory but to have coherent mesh
    #rem does not work for 2D meshes normals need to be added manually (works like a texture)
    mesh.updateNormals()
    if header is not None:
        #fill the mesh empty header of the mesh with values in header
        h = mesh.header()
        for k in header.keys():
            h[k] = header[k]
    return mesh