import dolfin as df
import math
import matplotlib.pyplot as plt

from .define_markers import define_markers
from .convert_unit import convert_unit
from .get_mode_shape_and_frequency import get_mode_shape_and_frequency
from .define_eigen_solver import define_eigen_solver

import petsc4py

comm = df.MPI.comm_world
mpi_rank = df.MPI.rank(comm)  # rank of current processor
mpi_size = df.MPI.size(comm)  # total processors called


def comp_modeshape(mat_obj, mesh_obj, bc, save_path, neig):
    E = mat_obj.E
    rho = mat_obj.rho
    nu = mat_obj.nu

    Rext = mesh_obj.Rext
    Rint = mesh_obj.Rint

    if mesh_obj.h == 0.0:
        mesh = mesh_obj.create()
    elif mesh_obj.h > 0.0:
        mesh, cell_markers, facet_markers, tag_map = mesh_obj.load()

    cell_markers, facet_markers = define_markers(mesh, Rext, Rint)

    # save marker functions into files readable with Paraview
    df.File(save_path + "Marker_Functions/" + "cell_markers.pvd") << cell_markers
    df.File(save_path + "Marker_Functions/" + "facet_markers.pvd") << facet_markers

    # define subdomains and cell measurement
    dx = df.Measure("dx", domain=mesh, subdomain_data=cell_markers)

    # Parameters
    # Lame coefficient for constitutive relation
    def mu_func(E, nu):
        return E / 2.0 / (1.0 + nu)

    def lmbda_func(E, nu):
        return E * nu / (1.0 + nu) / (1.0 - 2.0 * nu)

    def E_func(mu, lmbda):
        return mu * (3.0 * lmbda + 2.0 * mu) / (lmbda + mu)

    def nu_func(mu, lmbda):
        return lmbda / (2.0 * (lmbda + mu))


    s_unit = "m"
    t_unit = "ms"
    w_unit = "kg"


    E = E*convert_unit(1.0, "kg", w_unit)/(convert_unit(1.0, "m", s_unit)*convert_unit(1.0, "s", t_unit)**2)
    rho = rho*convert_unit(1.0, "kg", w_unit)/(convert_unit(1.0, "m", s_unit)**3)

    mu = mu_func(E, nu)
    lmbda = lmbda_func(E, nu)

    # dimention
    dim = mesh.topology().dim()

    # mesh coordinate
    x_coord = mesh.coordinates()


    # strain tensor
    def eps(v):
        return df.sym(df.grad(v))

    # isotropic stress tensor
    def sigma(v):
        dim = v.geometric_dimension()
        return 2.0*mu*eps(v) + lmbda*df.tr(eps(v))*df.Identity(dim)


    # Define function space
    V = df.VectorFunctionSpace(mesh, "Lagrange", degree=1)
    du = df.TrialFunction(V)
    tu = df.TestFunction(V)

    # =========================== define eigenvalue problem ===========================
    # eigenvalue problem: [K]\{U\}=\lambda[M]\{U\}
    # eigenfrequency: \lambda=\omega^2
    k_form = df.inner(sigma(du), eps(tu))*dx
    l_form = df.Constant(1.0)*tu[0]*dx
    m_form = rho*df.dot(du, tu)*dx



    # =========================== Dirichlet Boundary Conditions ===========================

    if dim==2: 
        zero = df.Constant((0.0, 0.0))
    elif dim==3:
        zero = df.Constant((0.0, 0.0, 0.0))

    # clamped outside
    dbc1 = df.DirichletBC(V, zero, facet_markers, 1)

    # clamped inside
    dbc2 = df.DirichletBC(V, zero, facet_markers, 2)

    # clamped inside and outside
    dbc3 = [dbc1, dbc2]



    def simulation_isotropic_c(save_path, Dbc, neig):
        df.File(save_path + "Marker_Functions/" + "cell_markers.pvd") << cell_markers
        df.File(save_path + "Marker_Functions/" + "facet_markers.pvd") << facet_markers

        eigensolver, K, M = define_eigen_solver(k_form, l_form, m_form, Dbc, "c")

        eigensolver.solve(neig)

        # converged eigenvalues and number of iterations
        conv = eigensolver.get_number_converged()
        # no_of_iterations = eigensolver.get_iteration_number() # does not have this function

        if mpi_rank == 0:
            print("\nNumber of converged eigenvalues: {:3d}".format(conv))
            # print('\nNumber of iterations: {:3d}'.format(no_of_iterations))

        freqs = get_mode_shape_and_frequency(
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
        )
        return freqs

    def simulation_isotropic_ff(save_path, k_form, m_form, neig):
        df.File(save_path + "Marker_Functions/" + "cell_markers.pvd") << cell_markers
        df.File(save_path + "Marker_Functions/" + "facet_markers.pvd") << facet_markers
        eigensolver, K, M = define_eigen_solver(k_form, l_form, m_form, [], "ff")
        eigensolver.solve(neig)

        freqs = get_mode_shape_and_frequency(
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
        )
        return freqs


    if bc == "FF":
        save_path_1 = save_path + "free_free/"
        freqs = simulation_isotropic_ff(save_path_1, k_form, m_form, neig)
        

    if bc == "CF":
        save_path_1 = save_path + "clamped_free/"
        freqs = simulation_isotropic_c(save_path_1, dbc2, neig)

    if bc == "FC":
        save_path_1 = save_path + "free_clamped/"
        freqs = simulation_isotropic_c(save_path_1, dbc1, neig)

    if bc == "CC":
        save_path_1 = save_path + "clamped_clamped/"
        freqs = simulation_isotropic_c(save_path_1, dbc3, neig)

    return freqs

















