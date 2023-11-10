# TODO -- some thoroughout code, also:
# check z-averaging
# plot average only with/without CI
# alpha sliders
# thickness slider
# better positioning for popups
# export data
# patch editor
# target insertion
# figsave
# animator
# line smoothing
# directory structure flexibility
# shading/shadows on background
# ordered transparency
# glow effect

import numpy as np
import scipy.stats as st
from scipy.interpolate import CubicSpline

from visuals import Viz
import data_reader


class PlotParameters:
    def __init__(self, subjects, color, filter_types, avg_color, avg_bool, transform,
                 conf_int, normalisation, custom_filter_set):
        self.subjects = subjects
        self.color = color
        self.filter_types = filter_types
        self.avg_color = avg_color
        self.average = avg_bool
        self.transform = transform
        self.conf_int = conf_int
        self.normalisation = normalisation
        self.custom_filter_set = custom_filter_set


def cubic_resample(points, n_samples):
    cs = CubicSpline(np.linspace(0, n_samples, len(points)), points)
    resampled_points = cs(np.arange(n_samples))
    # return sampled_points.reshape((1, n_samples, 3))
    return resampled_points


def average_trajectories(points, conf_int, resample=0):
    all_i = [0]
    for i in range(len(points)):
        if np.all(np.isnan(points[i, :])):
            all_i += [i, i+1]
    assert all_i[-1] == len(points)
    n_samples = all_i[1]
    for i in range(0, len(all_i)-1, 2):
        try:
            assert all_i[i+1] - all_i[i] == n_samples 
        except AssertionError:
            print("Not all trajectories are same length. Try using resample.")
            return

    points_all = np.empty((0, n_samples, 3))
    for i in range(0, len(all_i)-1, 2):
        # TODO this and dependent code should be removed i think
        if resample:
            n_samples = resample
            points_all = np.concatenate((points_all,
                                         cubic_resample(points[all_i[i]:all_i[i+1]],
                                                        n_samples)).reshape((1, n_samples, 3)),
                                        axis=0)
        else:
            points_all = np.concatenate((points_all,
                                         points[all_i[i]:all_i[i+1]].reshape((1, n_samples, 3))),
                                        axis=0)

    mean_points = np.mean(points_all, axis=0)
    # TODO confidence variable??
    # TODO TODO check with someone about scale, shape?
    confidence = st.t.interval(conf_int,
                               len(points_all)-1,
                               loc=mean_points,
                               scale=st.sem(points_all))
    return mean_points, confidence


# def average_trajectories_with_resampling(points):
    # def resample(points, n_samples):
        # sampled_points = np.zeros((n_samples, 3))
        # for i in range(3):
            # sampled_points[:, i] = np.interp(np.linspace(0, len(points), n_samples),
                                             # np.arange(0, len(points)),
                                             # points[:, i])
        # return sampled_points.reshape((1, n_samples, 3))

    # # get length max length of a trajectory and indices of trajectories
    # max_sample = 0
    # all_i = [0]
    # for i in range(len(points)):
        # # print(points[i, :])
        # if np.all(np.isnan(points[i, :])):
            # dist = i - all_i[-1]
            # if dist > max_sample:
                # max_sample = dist
            # all_i += [i, i+1]
    # assert all_i[-1] == len(points)

    # # resample and combine
    # points_all = np.empty((0, max_sample, 3))
    # for i in range(0, len(all_i)-1, 2):
        # points_all = np.concatenate((points_all,
                                     # resample(points[all_i[i]:all_i[i+1]], max_sample)),
                                    # axis=0)

    # mean_points = np.mean(points_all, axis=0)
    # # TODO confidence variable??
    # # TODO TODO check with someone about scale, shape?
    # confidence = st.t.interval(0.95,
                               # len(points_all)-1,
                               # loc=mean_points,
                               # scale=st.sem(points_all))
    # return mean_points, confidence


def get_trajs(csv, path, filter=None, transform=None, resample=0):
    points_all = np.empty((0, 3))

    if transform == Transform.LR:
        transform_filter = get_transform_filter(csv, left=True)
    elif transform == Transform.RL:
        transform_filter = get_transform_filter(csv, left=False)
    else:
        transform_filter = None

    traj_fns = data_reader.get_traj_filenames(path)
    # TODO how to deal with first 16? -- default block 1 filer?
    for i in range(16, len(csv["trial_num"])):
        if filter is None or filter[i]:
            points = data_reader.get_traj_data(traj_fns[i])
            points = np.array(points).T
            # TODO resampling is a vanity thing now, resample = n_samples, 0 means don't
            if resample:
                points = cubic_resample(points, resample) 
            if transform_filter is not None and transform_filter[i]:
                points[:, 0] *= -1

            points_all = np.concatenate((points_all,
                                         points,
                                         np.array([[np.nan, np.nan, np.nan]])))

    return points_all


def select_by_congruency(results, congruent=True, order2=False):
    congruency = get_order2_congruency(results) if order2 else get_congruency(results)
    mask = congruency == "1" if congruent else congruency == "0"
    return mask


def select_by_location(results, left=True):
    field_name = "stimulus_location"
    location = np.array(results[field_name])
    mask = location == "1" if left else location == "2"
    return mask


# TODO could make this the standard for all
def select_by_custom(results, field_value_dict):
    mask = None
    for field_name, valid_values in field_value_dict.items():
        vals = np.array(results[field_name])
        if mask is None:
            mask = np.ones(vals.shape, dtype=bool)
        for i, val in enumerate(vals):
            if not (mask[i] and (val in valid_values or "Any" in valid_values)):
                mask[i] = False
    return mask


def get_possible_filters(base_path, subject):
    fname = base_path + subject + "/S001/trial_results.csv"
    csv = data_reader.get_results(fname)
    pf = {}
    for label in csv.columns:
        values = np.array(csv[label])
        possible_values = np.unique(values)
        possible_values = possible_values[possible_values != "xx"]
        # TODO IMPORTANT fix hack -- this is not always desired behaviour
        if len(possible_values) > 1 and len(possible_values) < 20:
            pf[label] = possible_values
    return pf


def normalise_z(lines, type):
    # mask = np.invert(np.isnan(lines[:, 2]))

    if type == 2:
        mask = np.zeros(lines[:, 2].shape)
        start_point = True
        current_start = 0
        for i, p in enumerate(lines[:, 2]):
            if start_point:
                current_start = p
                start_point = False
            if np.isnan(p):
                start_point = True
            else:
                mask[i] = current_start
    else:
        mask = lines[0, 2]
    lines[:, 2] -= mask


def get_transform_filter(results, left=True):
    field_name = "stimulus_location"
    location = np.array(results[field_name])
    field_name = "congruency"
    congruency = np.array(results[field_name])
    if left:
        mask = np.logical_or(np.logical_and(location == "1", congruency == "1"),
                             np.logical_and(location == "2", congruency == "0"))
    else:
        mask = np.logical_or(np.logical_and(location == "2", congruency == "1"),
                             np.logical_and(location == "1", congruency == "0"))
    return mask


def get_congruency(csv):
    field_name = "congruency"
    congruency = csv[field_name]
    return np.array(congruency)


def get_order2_congruency(csv):
    field_name = "congruency"
    congruency = csv[field_name]
    congruency = [""] + list(congruency)[:-1]
    return np.array(congruency)


class FilterType:
    CONGRUENT = 1
    CONGRUENT2 = 4
    INCONGRUENT = 2
    INCONGRUENT2 = 5
    LEFT = 7
    RIGHT = 8


class Transform:
    NONE = 0
    LR = 1
    RL = 2


class Visualizer():
    def __init__(self):
        self.base_path = "../data/VR-S1/Hand/"
        self.object_base_path = "../data/VR-S1/Objects/"
        self.subjects = data_reader.get_subjects(self.base_path)
        self.results = None
        self._viz = None
        self._plot_id_counter = 0
        self._target_id_counter = 0

    def add_viz(self, widget):
        self._viz = Viz(widget)

    def change_base_path(self, base_path):
        self.base_path = base_path
        self.subjects = data_reader.get_subjects(base_path)

    def get_filters(self, csv, filter_types, custom_filter_set):
        assert not (FilterType.CONGRUENT in filter_types 
                    and FilterType.INCONGRUENT in filter_types)
        assert not (FilterType.CONGRUENT2 in filter_types 
                    and FilterType.INCONGRUENT2 in filter_types)
        assert not (FilterType.LEFT in filter_types 
                    and FilterType.RIGHT in filter_types)
        masks = []
        if FilterType.CONGRUENT in filter_types:
            masks.append(select_by_congruency(csv, True, False))
        if FilterType.INCONGRUENT in filter_types:
            masks.append(select_by_congruency(csv, False, False))
        if FilterType.CONGRUENT2 in filter_types:
            masks.append(select_by_congruency(csv, True, True))
        if FilterType.INCONGRUENT2 in filter_types:
            masks.append(select_by_congruency(csv, False, True))
        if FilterType.LEFT in filter_types:
            masks.append(select_by_location(csv, True))
        if FilterType.RIGHT in filter_types:
            masks.append(select_by_location(csv, False))
        masks.append(select_by_custom(csv, custom_filter_set))

        mask = np.all(np.array(masks), axis=0)
        return mask

    def add_plot(self, pp: PlotParameters):
        lines_all = np.empty((0, 3))

        for subject in pp.subjects:
            # TODO this assumes the curent dir structure
            fname = self.base_path + subject + "/S001/trial_results.csv"
            results = data_reader.get_results(fname)
            filter = self.get_filters(results, pp.filter_types, pp.custom_filter_set)
            if not np.any(filter):
                continue

            lines = get_trajs(results, self.subjects[subject], filter, pp.transform)

            if pp.normalisation == 1:
                normalise_z(lines, 1)

            lines_all = np.concatenate((lines_all,
                                        lines))
        if lines_all.size == 0:
            print("Selected filters removed all subjects")
            return None
        if pp.normalisation == 2:
            normalise_z(lines_all, 2)

        self._plot_id_counter += 1
        self._viz.add_plot(self._plot_id_counter, lines_all, pp.color, order=3)
        if pp.average:
            average_points, confidence = average_trajectories(lines_all, pp.conf_int)
            # TODO how to do colors?
            self._viz.add_plot(self._plot_id_counter, average_points, pp.avg_color, width=14.)
            for cline in confidence:
                self._viz.add_plot(self._plot_id_counter, cline, pp.avg_color, width=7.)
            self._viz.add_confidence_ribbon(self._plot_id_counter, confidence, color=pp.avg_color)

        # self._viz.add_plot(self._plot_id_counter, lines_all, color, order=3,
                           # average_points=average_points)

        self._viz.recenter_camera()
        # TODO store data for export
        return self._plot_id_counter

    def remove_plot(self, plot_id):
        self._viz.remove_plot(plot_id)
        self._viz.recenter_camera()

    def remove_object(self, obj_id):
        self._viz.remove_object(obj_id)
        self._viz.recenter_camera()

    def change_plot_color(self, plot_id, color):
        self._viz.plots[plot_id][0].set_data(color=color)

    def change_object_color(self, obj_id, color):
        self._viz.targets[obj_id].mesh.color = color

    def add_target(self, x, y, z, size, shape, color):
        self._target_id_counter += 1
        self._viz.add_target(self._target_id_counter, x, y, z, size, shape, color)
        return self._target_id_counter

    def get_custom_filter_list(self):
        return get_possible_filters(self.base_path, list(self.subjects.keys())[0])
