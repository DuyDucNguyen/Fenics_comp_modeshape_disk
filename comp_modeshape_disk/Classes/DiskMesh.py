import dolfin as df
import matplotlib.pyplot as plt
from ..Methods.DiskMesh.create_simple_mesh import create_simple_mesh
from ..Methods.DiskMesh.create_mesh_with_holes import create_mesh_with_holes
from ..Methods.DiskMesh.convert_to_xdmf import convert_to_xdmf
from ..Methods.DiskMesh.read_xdmf import read_xdmf




class DiskMesh():
    """
        mesh object
        :param Rint: interior raidus
        :param Rext: exterior raidus
        :param res: mesh resolution
        :param Rholes: holes radius
        
    """
    def __init__(self, 
                Rint = 0, 
                Rext = 0, 
                Rholes = 0,
                res = 0,
                h = 0,
                load_path = 'load_path',
                mesh_name = 'mesh_name'
                ):

        self.Rint = Rint
        self.Rext = Rext
        self.Rholes = Rholes
        self.res = res
        self.h = h
        self.load_path = load_path
        self.mesh_name = mesh_name

    def create(self):
        if self.Rholes == 0:
            mesh = create_simple_mesh(self.Rint, self.Rext, self.res)
        if self.Rholes > 0:
            mesh = create_mesh_with_holes(self.Rint, self.Rext, self.Rholes, self.res)
        return mesh

    #def save(self):
    #   df.File(self.save_path + self.mesh_name) << self.create()
    #   return

    def load(self):
        head, tail = self.mesh_name.split('.')
        mesh_name = head + '.xdmf'
        mesh, cell_markers, facet_markers, tag_map = read_xdmf(self.load_path, mesh_name)
        return mesh, cell_markers, facet_markers, tag_map

    def convert_msh_to_xdmf(self):
        convert_to_xdmf(self.load_path, self.mesh_name, self.load_path)

    def plot(self):
        if self.h == 0:
            plt.figure()
            df.plot(self.create())
            plt.show()

