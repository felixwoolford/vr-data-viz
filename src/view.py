#UNUSED -- this should be where half of the stuff from gui.py goes
import core

class Intermediary:
    def __init__(self, visualizer: core.Visualizer,):
        self.visualizer = visualizer
        pass

    def set_fname(self, fname, obj):
        print("Selected", fname)
        if not obj:
            self.visualizer.change_base_path(fname + "/")
        else:
            self.visualizer.object_base_path = fname + "/"
