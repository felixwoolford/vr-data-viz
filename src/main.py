import gui
# import visuals
import core

if __name__ == "__main__":
    v = core.Visualizer()
    g = gui.GUI(v)
    # TODO this doesn't need to be like this
    frame = g._window.mf.new_visual_frame(None)
    v.add_viz(frame)
    frame.set_visual(v._viz)
    g.show_windows()
    # Start up the GUI app - end of the line for the main thread
    g._begin()
