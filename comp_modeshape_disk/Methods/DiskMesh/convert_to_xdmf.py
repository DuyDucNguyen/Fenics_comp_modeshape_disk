from dolfin import *
import meshio
import pandas as pd
import inspect
import sys

comm = MPI.comm_world
mpi_rank = MPI.rank(comm)  # rank of current processor
mpi_size = MPI.size(comm)  # total processors called


cell_types_3d = ["tetra", "wedge", "hexahedron"]
cell_types_2d = ["quad", "triangle"]
cell_types_1d = ["line"]


# print('fenics_meshio_convert_to_xdmf')
# print(load_path)
# print(mesh_name)
# print(save_path)


def convert_to_xdmf(load_path, mesh_name, save_path):
    # print('\nfenics_meshio_convert_to_xdmf')
    # print(load_path)
    # print(mesh_name)
    # print(save_path)
    if mpi_rank == 0:
        print("\n=== {} ===".format(inspect.stack()[0][3]))
    if mpi_rank == 0:
        print("file name:", mesh_name)

    head_name, tail_name = mesh_name.split(".")

    # meshio reads .msh mesh
    meshio_mesh = meshio.read(load_path + mesh_name)

    # meshio extract mesh data
    cell_data = meshio_mesh.cell_data  # gmsh tags
    field_data = (meshio_mesh.field_data)  # dictionary: 'physical group name': [meshio number, dim]
    cells_dict = meshio_mesh.cells_dict  # dictionary: 'cell type': [nodesID]
    cell_data_dict = (meshio_mesh.cell_data_dict)  # dictionary: 'gmsh:physical': {]'cell type':[tag number]}

    # print(cell_data)
    # print(field_data)
    # print(cells_dict)
    # print(cell_data_dict)

    field_data_str = [
        "name:'{}' tag:{} dim:{}".format(key, field_data[key][0], field_data[key][1])
        for key in field_data.keys()
    ]

    mtype3d = [key for key in cells_dict.keys() if (key in cell_types_3d) == True]
    mtype2d = [key for key in cells_dict.keys() if (key in cell_types_2d) == True]
    mtype1d = [key for key in cells_dict.keys() if (key in cell_types_1d) == True]

    mtype = {"1": mtype1d, "2": mtype2d, "3": mtype3d}

    # define dimension of the geometry
    if len(mtype3d) != 0:
        dim = 3
    elif len(mtype2d) != 0:
        dim = 2
    elif len(mtype1d) != 0:
        dim = 1
    if mpi_rank == 0:
        print("dim:", dim)

    # print
    if bool(field_data) == False:  # empty dict
        if mpi_rank == 0:
            print("Meshio: mesh has number tags")
    else:
        if mpi_rank == 0:
            print("Meshio: mesh has string tags")
    if mpi_rank == 0:
        # print('cell_dict:', cells_dict.keys())
        print("1d cell type:", mtype1d)
        print("2d cell type:", mtype2d)
        print("3d cell type:", mtype3d)
        [print(ele) for ele in field_data_str]

    # define tag_map: string name, number, dimension
    tag_map = [(key, field_data[key][0], field_data[key][1]) for key in field_data.keys()]

    # export tag_map as csv
    df = pd.DataFrame(field_data)
    df.to_csv(save_path + head_name + "_tag_map.csv", index=False, header=True)

    # meshio write body cells
    for ele in mtype[str(dim)]:
        meshio.write(
            save_path + head_name + ".xdmf",
            meshio.Mesh(points=meshio_mesh.points, cells={ele: cells_dict[ele]}),
        )

    # meshio write cell_markers
    cell_type = mtype[str(dim)][0]
    if "gmsh:physical" in cell_data_dict.keys():
        cell_markers_data = meshio.Mesh(
            points=meshio_mesh.points,
            cells=[(cell_type, cells_dict[cell_type])],
            cell_data={"name_to_read": [cell_data_dict["gmsh:physical"][cell_type]]},
        )
        meshio.write(save_path + head_name + "_cell_markers.xdmf", cell_markers_data)
    else:
        if mpi_rank == 0:
            print(
                "there is no 'gmsh:physical' in the mesh file, cell_markers is not created"
            )

    # meshio write facet_markers
    if mtype[str(dim - 1)] != []:
        facet_type = mtype[str(dim - 1)][0]
        if "gmsh:physical" in cell_data_dict.keys():
            facet_markers_data = meshio.Mesh(
                points=meshio_mesh.points,
                cells=[(facet_type, cells_dict[facet_type])],
                cell_data={
                    "name_to_read": [cell_data_dict["gmsh:physical"][facet_type]]
                },
            )
            meshio.write(
                save_path + head_name + "_facet_markers.xdmf", facet_markers_data
            )
        else:
            if mpi_rank == 0:
                print(
                    "there is no 'gmsh:physical' in the mesh file, facet_markers is not created"
                )
    else:
        if mpi_rank == 0:
            print(
                "mtype['{}']=".format(str(dim - 1)),
                mtype[str(dim - 1)],
                "facet_markers is not created",
            )

    return

