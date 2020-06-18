import comp_modeshape_disk as cmd
from comp_modeshape_disk.Classes.DiskMesh import DiskMesh
from comp_modeshape_disk.Classes.Material import Material
from comp_modeshape_disk.Classes.Simulation import Simulation
import dolfin as df
import matplotlib.pyplot as plt
import math


# TODO: use gmsh_api to generate 3D mesh

# ======
# Mesh Object
# ======
# 2D annular disk
Rint = 0.04     #[m] inner radius
Rext = 0.1      #[m] outer radius
Rholes = 0.0    #[m] holes radius
res = 80        #[m] resolution
mesh2d_obj = DiskMesh(Rint=Rint, 
                      Rext=Rext, 
                      Rholes=Rholes, 
                      res=res)
#mesh2d_obj.plot()

# 3D annular disk
Rint = 0.04     #[m] inner radius
Rext = 0.1      #[m] outer radius
Rholes = 0.0    #[m] holes radius
h = 0.005       #[m] thickness
mesh3d_obj = DiskMesh(Rint=Rint,
                      Rext=Rext,
                      h=h,
                      load_path='Geometry/',
                      mesh_name='annular_disk_3d.msh')   # load GMSH mesh
#mesh3d_obj.convert_msh_to_xdmf()
#mesh3d_obj.load()

# ======
# Material Object
# ======
# Material properties taken from Mohammad2017
E = 72000*1e6       # [kg/m/s**2] Young moduls
nu = 0.3            # [#] Poisson ratio
rho = 2800          # [kg/m^3] density
mat_obj = Material(E, nu, rho)


# ======
# Simulation Object
# ======
# boundary conditions 'C': clamped, 'F': free
# neig: number of eigen value
for bc in ['CF', 'FF', 'CC', 'FC']:  
    simu2d = Simulation(mesh_obj = mesh2d_obj, 
                  mat_obj = mat_obj,
                  bc = bc,
                  save_path = 'Simulation2D/',
                  neig = 20
                  )
    simu2d.run()
    simu3d = Simulation(mesh_obj = mesh3d_obj, 
                  mat_obj = mat_obj,
                  bc = bc,
                  save_path = 'Simulation3D/',
                  neig = 20
                  )
    simu3d.run()















