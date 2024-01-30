# TODO
# empty data handling
# figsave
# selectable sets for qa
# update legend
# averageing qa

import numpy as np
import scipy.stats as st
from scipy.interpolate import CubicSpline

from matplotlib.pyplot import color_sequences

from visuals import Viz
import data_reader


class PlotParameters:
    def __init__(self, label, subjects, color, filter_types, avg_color,
                 avg_bool, transform, conf_int, normalisation, custom_filter_set,
                 qap=False, n_bins=5, sort_field=None, qa_alpha=0.8):
        self.label = label
        self.subjects = subjects
        self.color = color
        self.filter_types = filter_types
        self.avg_color = avg_color
        self.average = avg_bool
        self.transform = transform
        self.conf_int = conf_int
        self.normalisation = normalisation
        self.custom_filter_set = custom_filter_set
        self.plot_changed = []
        self.qap = qap
        self.n_bins = n_bins
        self.sort_field = sort_field
        self.qa_alpha = qa_alpha


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


def get_qa_trajs(quintiled_dframes, path, transform):
    lines_set = []
    for quintile in quintiled_dframes:
        lines = get_trajs(quintile, path, transform=transform)
        # TODO magic no for conf int. Don't think we need to worry
        average_points, confidence = average_trajectories(lines, 0.95)
        lines_set.append(np.concatenate((np.empty((0, 3)), 
                                         average_points,
                                         np.array([[np.nan, np.nan, np.nan]])
                                         )))
        # lines_set.append(np.concatenate((np.empty((0, 3)), lines)))
    return lines_set, average_points.shape[0]


def get_trajs(csv, path, filter=None, transform=None, resample=0):
    points_all = np.empty((0, 3))

    if transform == Transform.LR:
        transform_filter = get_transform_filter(csv, left=True)
    elif transform == Transform.RL:
        transform_filter = get_transform_filter(csv, left=False)

    traj_fns = data_reader.get_traj_filenames(path)
    for transform_i, i in enumerate(csv.index):
        if filter is None or filter[i]:
            points = data_reader.get_traj_data(traj_fns[i])
            points = np.array(points).T
            # TODO resampling is a vanity thing now, resample = n_samples, 0 means don't
            if resample:
                points = cubic_resample(points, resample) 
            if transform in [Transform.LR, Transform.RL] and transform_filter[transform_i]:
                points[:, 0] *= -1
            # TODO -- can remove permanently
            # if q is not None and qa_normalisation:
                # special_qa_transformation(points, q, qa_width)

            points_all = np.concatenate((points_all,
                                         points,
                                         np.array([[np.nan, np.nan, np.nan]])))

    # TODO -- can remove permanently
    # if q is not None and not qa_normalisation:
        # special_qa_transformation(points_all, q, qa_width)
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


def normalise_qap_z(lines, type):
    # mask = np.invert(np.isnan(lines[:, 2]))

    if type == 2:
        pass
        # mask = np.zeros(lines[:, 2].shape)
        # start_point = True
        # current_start = 0
        # for i, p in enumerate(lines[:, 2]):
            # if start_point:
                # current_start = p
                # start_point = False
            # if np.isnan(p):
                # start_point = True
            # else:
                # mask[i] = current_start
    else:
        mask = lines[0][0, 2]
        for line in lines:
            line[:, 2] -= mask

    # lines[:, 2] -= mask


# TODO for now, just force this to always happen
# hardcoded
def get_block1_filter(results):
    blocks = np.array(results["block_num"])
    mask = blocks != "1"
    return mask


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
    def __init__(self, data_path="../data/VR-S1/"):
        self.data_path = data_path
        self.base_path = self.data_path + "Hand/"
        self.object_base_path = self.data_path + "Objects/"
        self.export_base_path = self.data_path + "Exports/"
        self.pp_keyword = "fda_x"
        self.log_keyword = "fda_x"
        self.subjects, self.logs = data_reader.get_subjects(self.base_path, 
                                                            self.pp_keyword,
                                                            self.log_keyword)
        self.results = None
        self._viz = None
        self._plot_id_counter = 0
        self._target_id_counter = 0
        self.pp_set = {}
        self.data_for_export_set = {}
        self.cseqs = list(color_sequences.keys())
        self.color_seq = "Set2"

    def add_viz(self, widget):
        self._viz = Viz(widget)

    def change_data_path(self, data_path):
        self.data_path = data_path
        self.change_base_path(data_path + "Hand/")

    def change_base_path(self, base_path):
        self.base_path = base_path
        self.subjects, self.logs = data_reader.get_subjects(self.base_path, 
                                                            self.pp_keyword,
                                                            self.log_keyword)

    # TODO i think if someone makes some trajectories, keeps them, and then changes 
    # the keywords to make those trajectories invalid, we might get a crash if they then edit
    def change_keyword(self, example, log=False):
        keyword = example.split("/")[-1]
        number_split = None
        for c in keyword:
            if c.isdigit():
                number_split = c
                break
        if number_split is None:
            return False
        keyword = keyword.split(number_split)[0]
        if log:
            old = self.log_keyword
            self.log_keyword = keyword
        else:
            old = self.pp_keyword
            self.pp_keyword = keyword
        self.change_base_path(self.base_path)
        if len(self.subjects) == 0:
            if log:
                self.log_keyword = old
            else:
                self.pp_keyword = old
            self.change_base_path(self.base_path)
            return False
        return True

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
        # TODO hardcoding
        masks.append(get_block1_filter(csv))

        mask = np.all(np.array(masks), axis=0)
        return mask

    def add_plot(self, pp: PlotParameters):
        lines_all = np.empty((0, 3))

        for subject in pp.subjects:
            # TODO this assumes the curent dir structure
            fname = self.base_path + subject + "/S001/trial_results.csv"
            results = data_reader.get_results(fname)
            log_fname = self.logs[subject]
            logs = data_reader.get_results(log_fname)
            results = data_reader.concat_rl(results, logs)
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
            self.add_average(pp, self._plot_id_counter, lines_all)

        # self._viz.add_plot(self._plot_id_counter, lines_all, color, order=3,
                           # average_points=average_points)

        self._viz.recenter_camera()

        self.pp_set[self._plot_id_counter] = pp

        return self._plot_id_counter

    def export_data(self, label):
        data_reader.export_qa_data(self.data_for_export_set[label], self.export_base_path)

    def edit_plot(self, pp: PlotParameters, plot_id):
        self.pp_set[plot_id] = pp
        if "plots" in pp.plot_changed:
            self.remove_plot(plot_id)
            try:
                del self.data_for_export_set[pp.label]
            except KeyError:
                try:
                    del self.data_for_export_set[pp.old_label]
                except AttributeError:
                    pass
                except KeyError:
                    print("missing data? TODO")
            # return new plot_id to replace in the gui
            return self.add_plot(pp)
        if "qap" in pp.plot_changed:
            self.remove_plot(plot_id)
            try:
                del self.data_for_export_set[pp.label]
            except KeyError:
                try:
                    del self.data_for_export_set[pp.old_label]
                except AttributeError:
                    pass
                except KeyError:
                    print("missing data? TODO")
            # return new plot_id to replace in the gui
            return self.perform_analysis(pp)
        # NOTE this has to come before average removed because of how data works
        if "label" in pp.plot_changed:
            self.data_for_export_set[pp.label] = self.data_for_export_set[pp.old_label]
            self.data_for_export_set[pp.label]["label"] = pp.label
            del self.data_for_export_set[pp.old_label]
        # NOTE this has to come before average added because of how changing conf int works
        if "average removed" in pp.plot_changed:
            self._viz.remove_average_from_plot(plot_id)
            try:
                del self.data_for_export_set[pp.label]
            except KeyError:
                del self.data_for_export_set[pp.old_label]
        if "average added" in pp.plot_changed:
            lines_all = self._viz.plots[plot_id][0].pos
            self.add_average(pp, plot_id, lines_all)
        if "col" in pp.plot_changed:
            self.change_plot_color(plot_id, pp.color)
        if "avg col" in pp.plot_changed:
            self.change_avg_color(plot_id, pp.avg_color)
        if "alpha" in pp.plot_changed:
            self.change_qap_alpha(plot_id, pp.qa_alpha)
        return plot_id

    def add_average(self, pp, plot_id, lines):
        average_points, confidence = average_trajectories(lines, pp.conf_int)
        self._viz.add_plot(plot_id, average_points, pp.avg_color, width=14.)
        for cline in confidence:
            self._viz.add_plot(plot_id, cline, pp.avg_color, width=7.)
        self._viz.add_confidence_ribbon(plot_id, confidence, color=pp.avg_color)
        # TODO extend this with what is needed
        # TODO if qa gets sent into here, we need to check for it
        self.data_for_export_set[pp.label] = {"label": pp.label,
                                              "type": "average trajectory",
                                              "subjects": pp.subjects,
                                              "average": average_points,
                                              "confidence": confidence,
                                              "confidence interval": pp.conf_int,
                                              "filters": pp.filter_types,
                                              "extra_filters": pp.custom_filter_set,
                                              "transformations": pp.transform,
                                              "normalisation": pp.normalisation
                                              }

    def remove_plot(self, plot_id):
        self._viz.remove_plot(plot_id)
        self._viz.recenter_camera()

    def perform_analysis(self, qap: PlotParameters):
        n_bins = qap.n_bins
        lines_all = [np.empty((0, 3)) for i in range(n_bins)]
        for subject in qap.subjects:
            fname = self.base_path + subject + "/S001/trial_results.csv"
            base_csv = data_reader.get_results(fname)
            log_fname = self.logs[subject]
            logs = data_reader.get_results(log_fname)
            base_csv = data_reader.concat_rl(base_csv, logs)
            filter = self.get_filters(base_csv, qap.filter_types, qap.custom_filter_set)

            if not np.any(filter):
                print("TODO -- manage what happens when invalid filter set applied")
                return

            # sort
            # TODO -- is numeric always wanted -- currently is always?
            # print(subject)
            base_csv[qap.sort_field] = base_csv[qap.sort_field].astype(float)
            csv = base_csv[filter].sort_values(qap.sort_field)

            # divide
            rows = len(csv.index)
            n_extras = rows % n_bins
            bigger_bins = sorted(np.random.choice(range(n_bins), n_extras, replace=False))
            bin_size = rows // n_bins
            indices = [0]
            extras = 0
            for i in range(n_bins):
                bigbin = i in bigger_bins
                indices.append((i+1) * bin_size + extras + int(bigbin))
                if bigbin: 
                    extras += 1
            indices2 = [list(range(indices[i], indices[i+1])) for i in range(n_bins)]
            quintiled_dframes = [csv.iloc[q] for q in indices2]
            q_ranges = [(csv.iloc[indices[i]][qap.sort_field], csv.iloc[indices[i+1]-1][qap.sort_field]) 
                        for i in range(n_bins)]
            # q_ranges.append((csv.iloc[indices[-1]][qap.sort_field], csv.iloc[csv.shape[0]-1][qap.sort_field]))
            # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                # print("qranges", indices, q_ranges)

            # plot
            # print(quintiled_dframes)
            lines_set, l_length = get_qa_trajs(quintiled_dframes, self.subjects[subject], qap.transform)
            if qap.normalisation == 1:
                normalise_qap_z(lines_set, 1)
            for i, line in enumerate(lines_set):
                lines_all[i] = np.concatenate((lines_all[i], line))

        # TODO need total normalisation

        self._plot_id_counter += 1
        self.pp_set[self._plot_id_counter] = qap
        # color_set = color_sequences[qap.colour_key]
        color_set = color_sequences[self.color_seq]
        for i, lines in enumerate(lines_all):
            color = color_set[i % len(color_set)]
            color_text = (*color, 0.8)
            color = (*color, qap.qa_alpha)
            self._viz.add_plot(self._plot_id_counter, lines, color, order=3)
            self._viz.qa_legend(qap.label, color_text, i, self._plot_id_counter)

        self.data_for_export_set[qap.label] = {"label": qap.label,
                                               "type": "quintile analysis",
                                               "subjects": qap.subjects,
                                               "n bins": qap.n_bins,
                                               "lines": lines_all,
                                               "sort field": qap.sort_field,
                                               # TODO this isn't sorted out for multiple
                                               "q ranges": q_ranges,
                                               "filters": qap.filter_types,
                                               "extra_filters": qap.custom_filter_set,
                                               "transformations": qap.transform,
                                               "normalisation": qap.normalisation,
                                               "length": l_length,
                                               }

        # TODO this needs to be worked to average across subs
        if qap.average:
            average_set = []
            for i, lines in enumerate(lines_all):
                color = color_set[i % len(color_set)]
                color2 = (*color, 0.2)  # TODO MAGIC NUMVER
                # TODO probably some refactoring with plot traj possible
                # TODO remove that hardcode like it is in the other. Probably bring pp over
                average_points, confidence = average_trajectories(lines, qap.conf_int)
                average_set.append((average_points, confidence))
            for average_points, confidence in average_set:
                self._viz.add_plot(self._plot_id_counter, average_points, color, width=14.)
                for cline in confidence:
                    self._viz.add_plot(self._plot_id_counter, cline, color, width=7.)
                self._viz.add_confidence_ribbon(self._plot_id_counter, confidence, color=color2)

        self._viz.recenter_camera()

        return self._plot_id_counter

    def remove_object(self, obj_id):
        self._viz.remove_object(obj_id)
        self._viz.recenter_camera()

    def change_plot_color(self, plot_id, color):
        self._viz.plots[plot_id][0].set_data(color=color)

    def change_avg_color(self, plot_id, color):
        for plot in self._viz.plots[plot_id][1:]:
            plot.set_data(color=color)

    def change_object_color(self, obj_id, color):
        self._viz.targets[obj_id].mesh.color = color

    def change_qap_alpha(self, plot_id, alpha):
        color_set = color_sequences[self.color_seq]
        # i = 0
        for i, line in enumerate(self._viz.plots[plot_id]):
            if "_line_visual" in vars(line):
                color = color_set[i % len(color_set)]
                color = (*color, alpha)  # TODO MAGIC NUMVER
                # line.color = color
                line.set_data(color=color)
                # i += 1
        # i = 0
        # for line in self._viz.plots[plot_id]:
            # if "_line_visual" not in vars(line):
                # color = color_set[i % len(color_set)]
                # color = (*color, alpha)  # TODO MAGIC NUMVER
                # # line.color = color
                # line.color = color
                # i += 1

    def add_target(self, x, y, z, size, shape, color):
        self._target_id_counter += 1
        self._viz.add_target(self._target_id_counter, x, y, z, size, shape, color)
        return self._target_id_counter

    def get_custom_filter_list(self, qa=False):
        subject = next(iter(self.subjects.keys()))
        fname = self.base_path + subject + "/S001/trial_results.csv"
        csv = data_reader.get_results(fname)
        log_fname = self.logs[subject]
        logs = data_reader.get_results(log_fname)
        csv = data_reader.concat_rl(csv, logs)
        pf = {}
        for label in csv.columns:
            values = np.array(csv[label])
            possible_values = np.unique(values)
            possible_values = possible_values[possible_values != "xx"]
            if not qa:
                # TODO IMPORTANT fix hack -- this is not always desired behaviour
                if len(possible_values) > 1 and len(possible_values) < 20:
                    pf[label] = possible_values
            else:
                if values[-1].replace(".", "").replace("-", "").isnumeric() and len(possible_values) >= 5:
                    pf[label] = possible_values

        return pf
