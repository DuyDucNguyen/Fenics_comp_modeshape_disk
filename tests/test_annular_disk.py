import pytest
import numpy as np 

import sys
sys.path.append('../')

from comp_modeshape_disk.Classes.DiskMesh import DiskMesh
from comp_modeshape_disk.Classes.Material import Material
from comp_modeshape_disk.Classes.Simulation import Simulation




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

# 'CF', 'FF', 'CC', 'FC'
def test_3d_annular_disk_FF():
    simu3d = Simulation(mesh_obj = mesh3d_obj, 
                  mat_obj = mat_obj,
                  bc = 'FF',
                  save_path = 'Simulation3D/',
                  neig = 10
                  )
    freqs = simu3d.run()
    expect_freqs = [0.0, 0.0010090824026082607, 0.0011883452614546025, 0.0, 0.0017141825646661579, 0.0, 1101.380011496159, 1108.4001836577906, 1984.4666027240462, 2840.4737466673837]
    assert freqs == expect_freqs

