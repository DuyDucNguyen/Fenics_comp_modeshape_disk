from dolfin import *
import meshio
import inspect
import os
import pandas as pd
import sys


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 1


comm = MPI.comm_world
mpi_rank = MPI.rank(comm)  # rank of current processor
mpi_size = MPI.size(comm)  # total processors called


cell_types_3d = ["tetra", "wedge", "hexahedron"]
cell_types_2d = ["quad", "triangle"]
cell_types_1d = ["line"]



def read_xdmf(load_path, mesh_name):
    if mpi_rank == 0:
        print("\n=== {} ===".format(inspect.stack()[0][3]))

    head_name, tail_name = mesh_name.split(".")

    # meshio reads .msh mesh
    meshio_mesh = meshio.read(load_path + mesh_name)

    # CellBlock type
    # Fenics only work with 1 type of body cell (no mixed element)
    cell_type = meshio_mesh.cells[0].type
    field_data = (meshio_mesh.field_data)  # dictionary: 'physical group name': [meshio number, dim]
    cells_dict = meshio_mesh.cells_dict  # dictionary: 'cell type': [nodesID]
    cell_data_dict = (meshio_mesh.cell_data_dict)  # dictionary: 'gmsh:physical': {]'cell type':[tag number]}

    # print(cell_data)
    # print(field_data)
    # print(cells_dict)
    # print(cell_data_dict)

    # define dimension of the geometry
    if cell_type in cell_types_3d:
        dim = 3
    elif cell_type in cell_types_2d:
        dim = 2
    elif cell_type in cell_types_1d:
        dim = 1
    if mpi_rank == 0:
        print("dim:", dim)

    # read mesh
    mesh = Mesh()
    with XDMFFile(load_path + mesh_name) as infile:
        infile.read(mesh)

    # read facet markers
    facet_fname = load_path + head_name + "_facet_markers.xdmf"
    if os.path.isfile(facet_fname):
        mvc = MeshValueCollection("size_t", mesh, dim - 1)  # facet
        with XDMFFile(facet_fname) as infile:
            infile.read(mvc, "name_to_read")
        facet_markers = cpp.mesh.MeshFunctionSizet(mesh, mvc)
    else:
        if mpi_rank == 0:
            print("facet_markers file does not exist")
        facet_markers = False

    # read cell markers
    cell_fname = load_path + head_name + "_cell_markers.xdmf"
    if os.path.isfile(cell_fname):
        mvc = MeshValueCollection("size_t", mesh, dim)  # cell
        with XDMFFile(cell_fname) as infile:
            infile.read(mvc, "name_to_read")
        cell_markers = cpp.mesh.MeshFunctionSizet(mesh, mvc)
    else:
        if mpi_rank == 0:
            print("cell_markers file does not exist")
        cell_markers = False

    # read tag_map
    tag_map_fname = load_path + head_name + "_tag_map.csv"

    if is_non_zero_file(tag_map_fname):
        tag_map = pd.read_csv(
            load_path + head_name + "_tag_map.csv", squeeze=True
        ).to_dict()
        # print
        if mpi_rank == 0:
            [
                print("name: {}, tag: {}, dim: {}".format(key, tag_map[key][0], tag_map[key][1]))
                for key in tag_map
            ]
    else:
        tag_map = {}

    return mesh, cell_markers, facet_markers, tag_map
