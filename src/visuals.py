import numpy as np
from vispy import scene
from vispy.scene import Line, Sphere, Box
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import WireframeFilter
# from vispy.color import Colormap
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
            # self.view.camera = "arcball"
            self.view.camera = "turntable"
            # self.view.camera = "fly"

        if aspect is not None:
            self.view.camera.aspect = aspect
        self.range_ = range_
        if range_ is not None:
            self.view.camera.set_range(*range_)
            self.default_range = range_
        self.canvas.events.key_press.connect(self.key_pressed)
        # gloo.set_state("additive")

        self.render_background()

    # override this for key events
    def key_pressed(self, event):
        pass

    def render_background(self):
        points = np.array([[0, 0, 0],
                           [0, 1, 0],
                           [1, 0, 0],
                           [1, 1, 0],
                           ])
        faces = np.array([(i, i+1, i+2) for i in range(0, len(points)-2)])
        v_colors = np.array([[0.9, 0.9, 0.9, 0.3],
                            [0.6, 0.6, 0.6, 0.3],
                            [0.6, 0.6, 0.6, 0.3],
                            [0.3, 0.3, 0.3, 0.3],
                            ])

                # (len(points), 4))
        # v_colors[:, 3] = 0.1
        #TODO I should be transforming one mesh!
        # TODO TRANSPARENCY!!
        self.bg_xy = scene.visuals.Mesh(points, 
                                    faces, 
                                    vertex_colors=v_colors,
                                    shading=None,
                                        parent=self.view.scene,
                                        )
        points = np.array([[0, 1, 0],
                           [0, 1, 1],
                           [1, 1, 0],
                           [1, 1, 1],
                           ])
        self.bg_xz = scene.visuals.Mesh(points, 
                                    faces, 
                                    vertex_colors=v_colors,
                                    shading=None,
                                        parent=self.view.scene,
                                        )
        points = np.array([[0, 0, 0],
                           [0, 1, 0],
                           [0, 0, 1],
                           [0, 1, 1],
                           ])
        self.bg_yz = scene.visuals.Mesh(points, 
                                    faces, 
                                    vertex_colors=v_colors,
                                    shading=None,
                                        parent=self.view.scene,
                                        )
        self.bg_xy.attach(WireframeFilter(width=1))
        self.bg_xy.set_gl_state("translucent", depth_test=False)
        self.bg_xz.attach(WireframeFilter(width=1))
        self.bg_xz.set_gl_state("translucent", depth_test=False)
        self.bg_yz.attach(WireframeFilter(width=1))

        self.bg_yz.set_gl_state("translucent", depth_test=False)

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
        # self.volume_test()
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

    # def volume_test(self):
        # self.samples = 100

        # def vol(x, z):
            # if (z < 0.5 + (0.1**2 - (x - 0.5)**2)**0.5 and z > 0.5 - (0.1**2 - (x - 0.5)**2)**0.5):
                # return (1 / (np.linalg.norm([0.5,0.5]) - np.linalg.norm([x-0.5, z-0.5])))
            # else:
                # return 0.

        # X, Y, Z = (np.linspace(0.4, 0.6, self.samples),
                   # np.linspace(0.2, 0.6, self.samples),
                   # np.linspace(0.4, 0.6, self.samples)
                   # )

        # # print(X, Y, Z)
        # U = []
        # for z in Z:
            # for y in Y:
                # for x in X:
                    # f = vol(x, z)
                    # U.append(f)


        # colors = Colormap([[0,0,0,0.0],[1,1,1,0.1]], interpolation="linear")
        # vol1 = np.array(U).reshape(self.samples, self.samples, self.samples)

        # self.volume1 = scene.visuals.Volume(vol1, parent=self.view.scene, 
                                            # cmap=colors, method = 'translucent',
                                            # )

    # def highlight():
        # # TODO remove this cool glowy stuff or fix it
        # def find_nearest_point_heuristically(p, i):
            # max_j = len(average_points) - 1
            # d = np.linalg.norm(p - average_points[i])
            # h_range = 16
            # max_iter = 50
            # while h_range > 1:
                # max_iter -= 1
                # j = min(max_j, i + h_range)
                # k = max(0, i - h_range)
                # d2j = np.linalg.norm(p - average_points[j])
                # d2k = np.linalg.norm(p - average_points[k])
                # if d2j < d2k:
                    # d2 = d2j
                # else:
                    # d2 = d2k
                    # j = k

                # if d2 < d:
                    # d = d2
                    # h_range = 16
                    # i = j
                # else:
                    # h_range = h_range // 2
            # return d
        # def find_d_brutal(p):
            # d = np.linalg.norm(p - average_points[0])
            # for i in range(1, len(average_points)):
                # d2 = np.linalg.norm(p - average_points[i])
                # if d2 < d:
                    # d = d2
            # return d

        # color = np.ones((len(points), 4)) * color
        # i = 0
        # j = 0
        # # y = np.array([1, 0, 0, 1])
        # y = np.clip(color[0] ** (1/3) + np.array([0.8, 0.8, 0, 1]) ** 3, 0, 1)
        # y[3] = 1
        # mx = 0.01
        # if average_points is not None:
            # for point in points:
                # if np.all(np.isnan(point)):
                    # i = 0
                # else:
                    # # print(i, len(average_points))
                    # # ind = np.clip(int(i / (86 / 225)), 0, 225)
                    # # dist = np.linalg.norm(point - average_points[i])
                    # dist = find_nearest_point_heuristically(point, i)
                    # # dist = find_d_brutal(point)
                    # color[j] = ((y * np.clip((mx - dist) / mx, 0, 1))**2
                                # + (color[j] * np.clip(dist / mx, 0, 1))**2)**(1/2)
                    # i += 1
                # j += 1

    def add_plot(self, plot_id, points, color, width=2.0, order=1):
        traj = Line(points, color=color, width=width)
        traj.order = order
        # traj.set_gl_state("translucent", depth_test=False)
        # traj.set_depth_func('lequal')
        # use a list so average and maybe confidence intervals can include
        if plot_id in self.plots:
            self.plots[plot_id].append(traj)
        else:
            self.plots[plot_id] = [traj]
        traj.parent = self.view.scene
        # self.recenter_camera()

    def add_confidence_ribbon(self, plot_id, points, color):
        points = np.array(list(zip(points[0], points[1]))).reshape(int(points[0].size*2/3), 3)
        # faces = np.array([(i, i+1, i+3, i+2) for i in range(0, len(points)-3, 2)])
        faces = np.array([(i, i+1, i+2) for i in range(0, len(points)-2)])
        # TODO inexplicable error occured here where color appeared to be 5 values...
        v_colors = np.ones((len(points), 4)) * color
        v_colors[:, 3] *= 0.4
        ribbon = scene.visuals.Mesh(points, 
                                    faces, 
                                    vertex_colors=v_colors,
                                    shading=None)
        ribbon.order = 2
        # ribbon.set_gl_state("translucent", depth_test=False)
        if plot_id in self.plots:
            self.plots[plot_id].append(ribbon)
        else:
            self.plots[plot_id] = [ribbon]
        ribbon.parent = self.view.scene

    def remove_plot(self, plot_id):
        for plot in self.plots[plot_id]:
            plot.parent = None
        del self.plots[plot_id]

    def remove_object(self, target_id):
        self.targets[target_id].parent = None
        del self.targets[target_id]

    def set_plots(self, lines):
        # lines.parent = self.view.scene
        # lines.draw()
        # for line in self.plots:
            # line.parent = None
        # self.plots = lines
        for line in lines:
            line.parent = self.view.scene

    def recenter_camera(self):
        absmins = np.array([np.inf] * 3)
        absmaxs = np.array([-np.inf] * 3)
        print(self.plots)
        for plot_list in self.plots.values():
            for plot in plot_list:
                if type(plot) is Line:
                    pos = plot.pos
                    mins = np.min(pos[np.invert(np.any(np.isnan(pos), axis=1))], axis=0)
                    maxs = np.max(pos[np.invert(np.any(np.isnan(pos), axis=1))], axis=0)
                    absmins = np.min((absmins, mins), axis=0)
                    absmaxs = np.max((absmaxs, maxs), axis=0)
        for obj in self.targets.values():
            pos = obj._transform.translate[:3]
            absmins = np.min((absmins, pos), axis=0)
            absmaxs = np.max((absmaxs, pos), axis=0)

        center = (absmins + absmaxs) / 2
        # width = np.max(maxs - mins)

        self.view.camera.center = center
        # self.view.camera.scale_factor = 10
        # TODO FIX
        self.view.camera.scale_factor = .75

        points = np.array([[absmins[0], absmins[1], absmins[2]],
                           [absmins[0], absmaxs[1], absmins[2]],
                           [absmaxs[0], absmins[1], absmins[2]],
                           [absmaxs[0], absmaxs[1], absmins[2]],
                           ])
        faces = np.array([(i, i+1, i+2) for i in range(0, len(points)-2)])
        v_colors = np.array([[0.9, 0.9, 0.9, 0.3],
                             [0.6, 0.6, 0.6, 0.3],
                             [0.6, 0.6, 0.6, 0.3],
                             [0.3, 0.3, 0.3, 0.3]
                             ])
        self.bg_xy.set_data(points, faces, vertex_colors=v_colors)
        points = np.array([[absmins[0], absmaxs[1], absmins[2]],
                           [absmins[0], absmaxs[1], absmaxs[2]],
                           [absmaxs[0], absmaxs[1], absmins[2]],
                           [absmaxs[0], absmaxs[1], absmaxs[2]],
                           ])
        self.bg_xz.set_data(points, faces, vertex_colors=v_colors)
        points = np.array([[absmins[0], absmins[1], absmins[2]],
                           [absmins[0], absmaxs[1], absmins[2]],
                           [absmins[0], absmins[1], absmaxs[2]],
                           [absmins[0], absmaxs[1], absmaxs[2]],
                           ])
        self.bg_yz.set_data(points, faces, vertex_colors=v_colors)
        # points = np.array([[0, 0, 0],
                           # [0, 1, 0],
                           # [0, 0, 1],
                           # [0, 1, 1],
                           # ])

    def add_target(self, target_id, x, y, z, size, shape, color):
        if shape == "sphere":
            target = Sphere(radius=size, color=color, shading="smooth")
        elif shape == "cube":
            target = Box(size, size, size, color=color, edge_color="black",)
        # target.set_gl_state("translucent", depth_test=False)
        target.transform = STTransform(translate=[x, y, z])
        target.parent = self.view.scene
        self.targets[target_id] = target
        self.recenter_camera()

