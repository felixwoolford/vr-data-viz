from vispy import scene
from vispy.scene import Line, Sphere
from vispy.visuals.transforms import STTransform

# import core
# import numpy as np

# Base class for general model visualizations
class BaseVispy:
    frontend = "vispy"

    def __init__(self, widget, axes=False, range_ = None, interactive=True, aspect = None, **kwargs):
        self.canvas = scene.SceneCanvas(
            keys="interactive", parent=widget, show=True, bgcolor="#000000"
        )
        if axes:
            self.init_axes(**kwargs)
        else:
            self.view = self.canvas.central_widget.add_view()
            self.view.camera = "fly"

        if aspect is not None:
            self.view.camera.aspect = aspect
        self.range_ = range_
        if range_ is not None:
            self.view.camera.set_range(*range_)
            self.default_range = range_
        self.canvas.events.key_press.connect(self.key_pressed)

    # override this for key events
    def key_pressed(self, event):
        pass

    def init_axes(self, **kwargs):
        self.grid = self.canvas.central_widget.add_grid(margin=10)
        self.grid.spacing = 0
        self.r = 0

        self.title = scene.Label(kwargs.get("title", ""), color="w")
        self.title.height_max = 40
        self.grid.add_widget(self.title, row=0, col=0, col_span=2)
        self.r += 1
        self.yaxis = scene.AxisWidget(
            orientation="left",
            axis_label=kwargs.get("y_label", ""),
            axis_font_size=10,
            axis_label_margin=40,
            tick_label_margin=15,
        )
        self.yaxis.width_max = 80
        self.grid.add_widget(self.yaxis, row=self.r, col=0)

        self.xaxis = scene.AxisWidget(
            orientation="bottom",
            axis_label=kwargs.get("x_label", ""),
            axis_font_size=10,
            axis_label_margin=40,
            tick_label_margin=15,
        )
        self.xaxis.height_max = 80
        self.grid.add_widget(self.xaxis, row=self.r+1, col=1)

        right_padding = self.grid.add_widget(row=self.r, col=2, row_span=1)
        right_padding.width_max = 50

        self.view = self.grid.add_view(row=self.r, col=1, border_color="white")
        self.view.camera = "panzoom"
        self.view.camera.set_default_state()

        self.xaxis.link_view(self.view)
        self.yaxis.link_view(self.view)

    def iterate(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


class Viz(BaseVispy):
    def __init__(self, widget):
        super().__init__(widget, axes=False)
        self.plots = {} 
        self.targets = {}
        # self.plots = core.get_all()
        # for line in self.plots:
            # line.parent = self.view.scene
        # self.plots = []
        # for i in range(100):
            # self.plots.append(get_line1(i))
            # self.plots[-1].parent = self.view.scene

        # points1 = np.array([[1,1,1], [2,2,2], [np.nan, np.nan,np.nan], [3,3,3], [4,4,4]])
        # print(points1.shape)
        # points = np.empty((0,3))
        # print(points.shape)
        # points = np.concatenate((points,np.array([[1,1,1], [2,2,2]])))
        # points = np.concatenate((points,np.array([[np.nan, np.nan,np.nan], [3,3,3], [4,4,4]])))
        # print(points.shape)
        # # points = np.array([[[1,1,1], [2,2,2], [np.nan, np.nan,np.nan], [3,3,3], [4,4,4]]])
        # line = Line(points, color=[0.7, 0.2, 0, 0.4], width=4.0, parent=self.view.scene)

    def add_plot(self, plot_id, points, color):
        traj = Line(points, color=color, width=4.0)
        self.plots[plot_id] = traj
        traj.parent = self.view.scene

    def remove_plot(self, plot_id):
        self.plots[plot_id].parent = None

    def set_plots(self, lines):
        # lines.parent = self.view.scene
        # lines.draw()
        # for line in self.plots:
            # line.parent = None
        # self.plots = lines
        for line in lines:
            line.parent = self.view.scene

    def add_target(self, target_id, x, y, z, color):
        target = Sphere(radius=0.05, color=color, shading="smooth")
        target.transform = STTransform(translate=[x, y, z])
        target.parent = self.view.scene
        self.targets[target_id] = target


