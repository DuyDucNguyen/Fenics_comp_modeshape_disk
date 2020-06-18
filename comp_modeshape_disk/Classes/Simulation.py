from ..Methods.Simulation.comp_modeshape import comp_modeshape




mesh_obj = -1
mat_obj = -1


class Simulation():
    def __init__(self, 
                 mesh_obj = mesh_obj,
                 mat_obj = mat_obj,
                 bc = 'CF',
                 save_path = 'save_path',
                 neig = 1
                ):
        self.mat_obj = mat_obj
        self.mesh_obj = mesh_obj
        self.bc = bc
        self.save_path = save_path
        self.neig = neig

    def run(self):
        comp_modeshape(self.mat_obj, self.mesh_obj, self.bc, self.save_path, self.neig)
        return