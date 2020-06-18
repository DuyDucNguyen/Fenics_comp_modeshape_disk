import dolfin as df


def set_pmr_solver(K, M):
    # =========================== Solver setting ===========================
    # define solver
    # How to use
    # SLEPcEigenSolver(A): Create eigenvalue solver for Ax = \lambda x
    # SLEPcEigenSolver(A, B): Create eigenvalue solver Ax = \lambda Bx (Generalized Hermitian eigenvalue problem)

    eigensolver = df.SLEPcEigenSolver(K, M)  # Ku = \lambda Mu
    # print( help(SLEPcEigenSolver) )
    # print( help(eigensolver.get_options_prefix ) )

    # monitor SLEP solver
    # PETScOptions.set("eps_view")
    # PETScOptions.set("ksp_type", "cg")
    # PETScOptions.set("pc_type", "none")
    # PETScOptions.set("ksp_monitor_singular_value", "")

    # print(help(PETScOptions.set))
    # set solver's parameters
    pmr = eigensolver.parameters

    # solver setup 1
    pmr["problem_type"] = "gen_hermitian"
    pmr["tolerance"] = 1e-14
    pmr["spectral_transform"] = "shift-and-invert"  # needed
    pmr["spectral_shift"] = 0.0
    pmr["solver"] = "krylov-schur"
    #pmr['solver'] = 'lanczos' # too long, even parallelism is used

    
    return eigensolver


def define_solver_clamped(k_form, l_form, m_form, Dbc):
    K = df.PETScMatrix()  # stiffness matrix
    b = df.PETScVector()
    df.assemble_system(k_form, l_form, Dbc, A_tensor=K, b_tensor=b)
    M = df.PETScMatrix()  # mass matrix
    df.assemble(m_form, tensor=M)
    eigensolver = set_pmr_solver(K, M)
    return eigensolver, K, M


def define_solver_free_free(k_form, m_form):
    K = df.PETScMatrix()  # stiffness matrix
    df.assemble(k_form, tensor=K)
    M = df.PETScMatrix()  # mass matrix
    df.assemble(m_form, tensor=M)
    eigensolver = set_pmr_solver(K, M)
    return eigensolver, K, M


def define_eigen_solver(k_form, l_form, m_form, Dbc, typeBC):
    if typeBC == "c":  # clamped
        eigensolver, K, M = define_solver_clamped(k_form, l_form, m_form, Dbc)
        return eigensolver, K, M
    if typeBC == "ff":  # free free
        eigensolver, K, M = define_solver_free_free(k_form, m_form)
        return eigensolver, K, M
