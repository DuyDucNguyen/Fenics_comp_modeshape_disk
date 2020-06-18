import dolfin as df
import os
import numpy as np
import pandas as pd
from .convert_unit import convert_unit


comm = df.MPI.comm_world
mpi_rank = df.MPI.rank(comm)  # rank of current processor
mpi_size = df.MPI.size(comm)  # total processors called



def get_mode_shape_and_frequency(
    save_path,
    eigensolver,
    V,
    s_unit,
    t_unit,
    w_unit,
    E,
    nu,
    rho,
    neig,
    K,
    M,
    m_form,
    k_form,
):
    """
    Input:
        save_path: str 
        eigensolver: Eigen Solver 
        neig: int number 
    Output:
        save mode shape
        save natural frequency
    """

    # write results
    file = open(save_path + "material_and_frequencies.txt", "w")
    file.write("Target units Space: {}, Time: {}, Weight: {}\n".format(s_unit, t_unit, w_unit))
    file.write("E: {} [{}/({}.{}^2)]\n".format(E, w_unit, s_unit, t_unit))
    file.write("nu: {} [#]\n".format(nu))
    file.write("rho: {} [{}/{}^3]\n".format(rho, w_unit, s_unit))
    file.write("\n")
    

    # Extraction
    for i in range(neig):
        # Extract eigenpair i-th
        # vtk_u = File(save_path + 'Displacement/u{}/u{}.pvd'.format(i,i))
        # Set up file for exporting results
        file_results = df.XDMFFile(save_path + "Modeshape/u{}/u{}.xdmf".format(i, i))
        file_results.parameters["flush_output"] = True
        file_results.parameters["functions_share_mesh"] = True

        # r: real eigenvalue
        # c: complex eigenvalue
        # rx: real eigenvector
        # cx: complex eigenvector
        r, c, rx, cx = eigensolver.get_eigenpair(i)

        # 3D eigenfrequency (w^2=(2*pi*f)^2)
        freq = df.sqrt(r)/2/df.pi  # [Hz=1/s]

        # from ms to s
        freq = freq*1.0/convert_unit(1.0, t_unit, "s")

        if mpi_rank == 0:
            print("{0:d}) frequency {1:8.5f} [Hz]".format(i, freq))

        file.write("{0:d}) frequency {1:8.5f} [Hz]\n".format(i, freq))

        # Initialize function and assign eigenvector (renormalize by stiffness matrix)
        eigenmode = df.Function(V, name="Eigenvector" + str(i))
        eigenmode.vector()[:] = rx

        # NORMALIZED THE EIGENMODE BY MASS MATRIX
        # double check the eigenmode is already normalized by the mass matrix
        # subtitute the eigenmode into m_form and compute the integral which is equivalent to compute Phi^T*M*Phi
        # and the result should be 1
        # one = df.assemble(df.action(df.action(m_form, eigenmode), eigenmode))
        # print(one)

        # NORMALIZED THE EIGENMODE BY STIFFNESS MATRIX
        # Normalizing with the stiffness matrix can be done easily since K*u=omega^2*Mu and uMu=1 so that uKu=omega^2.
        # So if you define u'=u/omega then u'Ku' = 1.

        # vtk_u << (eigenmode, i)
        # vtk_u << eigenmode
        file_results.write(eigenmode)

    file.close()
