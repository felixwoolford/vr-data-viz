import sys

import gui

if __name__ == "__main__":
    # v = core.Visualizer()
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    g = gui.GUI(data_path)
    frame = g._window.mf.new_visual_frame(None)
    v = g._window.visualizer
    v.add_viz(frame)
    frame.set_visual(v._viz)
    g.show_windows()
    # Start up the GUI app - end of the line for the main thread
    g._begin()
