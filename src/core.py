import numpy as np
from vispy.scene import Line
# from vispy.visuals.collections.agg_segment_collection import AggSegmentCollection

from visuals import Viz
import data_reader


def get_line1(trial):
    csv = data_reader.get_results()
    points = data_reader.get_traj_data(csv, trial)
    points = np.array(points).T
    print(csv.columns)
    return Line(points, color=[0.7, 0.2, 0, 0.4], width=4.0)


def get_all(csv, fname):
    csv = data_reader.get_results(fname)
    path = "/" + "/".join(fname.split("/")[:-1]) + "/"
    # lines = []
    # colors = []
    # caps = [0]
    # line1 = AggSegmentCollection()
    points_all = np.empty((0,3))
    print(len(csv["trial_num"]))
    for i in range(len(csv["trial_num"])):
        points = data_reader.get_traj_data(csv, i, path)
        points = np.array(points).T
        points_all = np.concatenate((points_all, points, np.array([[np.nan, np.nan,np.nan]])))
        # line1.append(points[:-1], points[1:], caps=(0, len(points)-1), color=[0.7, 0.2, 0, 0.4], linewidth=4.0)
    # TODO shift this to the visual
    # lines.append(Line(points_all, color=[0.7, 0.2, 0, 0.4], width=4.0))
    return points_all
    # return Line(points, color=[0.7, 0.2, 0, 0.4], width=4.0)


class Visualizer():
    def __init__(self):
        self.base_path = "./"
        self.results = None
        self._viz = None
        self._plot_id_counter = 0
        self._target_id_counter = 0

    def add_viz(self, widget):
        self._viz = Viz(widget)

    # @property
    # def plot_id_counter(self):
        # self._plot_id_counter += 1
        # return self._plot_id_counter - 1

    # @property
    # def target_id_counter(self):
        # self._target_id_counter += 1
        # return self._target_id_counter - 1

    def open_data(self, fname):
        self.results = data_reader.get_results(fname)
        lines = get_all(self.results, fname)
        return lines

    def add_plot(self, fname, color):
        lines = self.open_data(fname)
        self._plot_id_counter += 1
        self._viz.add_plot(self._plot_id_counter, lines, color)
        return self._plot_id_counter

    def remove_plot(self, plot_id):
        self._viz.remove_plot(plot_id)

    def change_plot_color(self, plot_id, color):
        self._viz.plots[plot_id].set_data(color=color)

    def add_target(self, x, y, z, color):
        self._target_id_counter += 1
        self._viz.add_target(self._target_id_counter, x, y, z, color,)
        return self._target_id_counter

# // option B (pressing DEL activates the slots only when list widget has focus)
# QShortcut* shortcut = new QShortcut(QKeySequence(Qt::Key_Delete), listWidget);
# connect(shortcut, SIGNAL(activated()), this, SLOT(deleteItem()));
# }
# void MainWindow::deleteItem()
# {
    # delete listWidget->currentItem();
# }
