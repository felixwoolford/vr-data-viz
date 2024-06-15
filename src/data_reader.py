from pathlib import Path
import os

from datetime import datetime
import pandas as pd
# p_path = "../data/VR-S1/Hand/P01/S001/"
# results_fname = p_path + "trial_results.csv"


def get_traj_filenames(path):
    # Using practice of applying Path() at time of use
    return sorted([path+fname for fname in os.listdir(Path(path))])


def get_processed_data_dir(subject, path, keyword="fda_x"):
    try:
        pp_data_path = f"{path}/S001/{subject}/"
        valid_sets = []
        for s in sorted(os.listdir(Path(pp_data_path))):
            if os.path.isdir(Path(pp_data_path+s)):
                if keyword in s:
                    valid_sets.append(pp_data_path+s+"/")
        if not len(valid_sets):
            print(f"no {keyword} processed data for {subject}") 
            return None
        else:
            if len(valid_sets) > 1:
                print(f"too many {keyword} processed data for {subject}, selecting recent one") 
            return valid_sets[-1]
    except FileNotFoundError:
        print("PP invalid path found in data dir.")
        return None


def get_log_data_dir(subject, path, keyword="fda_x"):
    try:
        log_data_path = f"{path}/S001/{subject}/"
        log_data_path = get_specific_log_path(log_data_path, "log")
        valid_sets = []
        for s in sorted(os.listdir(Path(log_data_path))):
            if keyword in s:
                valid_sets.append(log_data_path+s+"/")
        if not len(valid_sets):
            print(f"no {keyword} log data for {subject}") 
            return None
        else:
            if len(valid_sets) > 1:
                print(f"too many {keyword} log data for {subject}, selecting recent one") 
            return valid_sets[-1]
    except FileNotFoundError:
        print("LOG invalid path found in data dir.")
        return None


def get_specific_log_path(path, keyword):
    for s in os.listdir(Path(path)):
        if os.path.isdir(Path(path+s)):
            if keyword in s:
                return path + s + "/"


def get_traj_data(traj_fname):
    # traj_field_name = "controllertracker_movement_location_0"
    # traj_fs = os.listdir(Path(path))
    # traj_fname = traj_fs[trial_id]
    # traj_fname = results_csv[traj_field_name][trial_id]

    # TODO rework for preprocessed I think??
    # filepath in data is incorrect and needs modifying
    # traj_fname = "/".join(traj_fname.split("/")[-2:])
    # traj_fname = path + traj_fname
    # print("filtered", traj_fname)

    traj_f = Path(traj_fname).open()
    traj_csv = pd.read_csv(traj_f)
    traj_x = list(traj_csv["pos_x"])
    # NOTE these two are flipped to align with standard graphics coordinates
    traj_y = list(traj_csv["pos_z"])
    traj_z = list(traj_csv["pos_y"])
    return (traj_x, traj_y, traj_z)


class ObjectShape:
    def __init__(self, object_id, x, y, z, size, shape, c):
        self.object_id = object_id
        self.x = x 
        # rotated like trajectories are
        self.y = z 
        self.z = y 
        self.size = size
        self.shape = shape
        self.c = c 


def get_object_data(fname):
    f = Path(fname).open()
    csv = pd.read_csv(f)
    objects = {}
    for row in csv.itertuples(index=False):
        obj = ObjectShape(row.object_id, row.x, row.y, row.z, row.size, row.shape, row.colour)
        objects[row.object_id] = obj
    return objects


def get_results(results_fname):
    results_f = Path(results_fname).open()
    return pd.read_csv(results_f, delimiter=",", dtype=str).fillna("xx")


def concat_rl(results, logs):
    concat = pd.concat([results, logs], axis=1, join="inner")
    concat = concat.loc[:, ~concat.columns.duplicated()]
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        # print(concat.iloc[2])
        # print(results, logs, concat)
    return concat


def get_subjects(base_path, pp_keyword, log_keyword, all=False):
    if all:
        # TODO make this a dict with the traj location
        return sorted([s for s in os.listdir(Path(base_path)) 
                       if os.path.isdir(Path(base_path+s))])
    else:
        subjects = {}
        logs = {}
        for s in os.listdir(Path(base_path)):
            path = base_path+s
            if os.path.isdir(Path(path)):
                pp_data_dir = get_processed_data_dir(s, path, pp_keyword)
                log_data_dir = get_log_data_dir(s, path, log_keyword)
                if pp_data_dir is not None and log_data_dir is not None:
                    # subjects[s] = f"{base_path}{s}/S001/{s}/{pp_data_dir}/"
                    subjects[s] = pp_data_dir
                    logs[s] = log_data_dir
        return subjects, logs


def export_qa_data(data, output_path):
    date_time = datetime.now().strftime("_%Y_%m_%d_%H_%M")
    path = output_path + data["label"] + date_time + "/"
    os.makedirs(Path(path), exist_ok=True)
    if data["type"] == "subject trajectory":
        ft = data["filtered_trials"]
        print(ft.items())
        print(max([len(trials) for sub, trials in ft.items()]), "ll")
        df_trials = pd.DataFrame(index=list(range(1, max([len(trials) for sub, trials in ft.items()])+1)))
        for subject, trials in ft.items():
            df_trials = df_trials.assign(**{str(subject): pd.Series(trials)})
        df_trials.to_csv(path+f"{data['label']}_trials_per_subject.csv")
        info = open(path+f"{data['label']}_info.csv", "w")
        # info.write("subjects, " + ", ".join(sorted(data["subjects"])) + "\n")
        ftypes = {1: "congruent only", 2: "incongruent only", 4: "following congruent only",
                  5: "following incongruent only", 7: "left target only", 8: "right target only"}
        info.write(f"basic_filters, {','.join([ftypes[i] for i in data['filters']])}\n")
        info.write(f"extra_filters, {data['extra_filters']}\n")
        # ttypes = {0: "none", 1: "to right", 2: "to left"}
        # info.write(f"transformation, {ttypes[data['transformations']]}\n")
        ntypes = {0: "none", 1: "by subject", 2: "total"}
        info.write(f"normalisation, {ntypes[data['normalisation']]}\n")
        info.close()

    elif data["type"] == "average trajectory":
        df_pos = pd.DataFrame(index=list(range(1, len(data["average"])+1)))
        df_pos = df_pos.assign(pos_x=data["average"][:, 0])
        df_pos = df_pos.assign(pos_y=data["average"][:, 2])
        # NOTE -- inverting back to the original data format -- see get_traj_data()
        df_pos = df_pos.assign(pos_z=data["average"][:, 1])
        df_pos = df_pos.assign(conf_min_x=data["confidence"][0][:, 0])
        df_pos = df_pos.assign(conf_min_y=data["confidence"][0][:, 1])
        df_pos = df_pos.assign(conf_min_z=data["confidence"][0][:, 1])
        df_pos = df_pos.assign(conf_max_x=data["confidence"][1][:, 0])
        df_pos = df_pos.assign(conf_max_y=data["confidence"][1][:, 1])
        df_pos = df_pos.assign(conf_max_z=data["confidence"][1][:, 1])

        df_pos.to_csv(path+f"{data['label']}_points.csv")

        info = open(path+f"{data['label']}_info.csv", "w")
        info.write("subjects, " + ", ".join(sorted(data["subjects"])) + "\n")
        # for subject in data["subjects"]:
        info.write(f"confidence_interval, {data['confidence interval']}\n")
        ftypes = {1: "congruent only", 2: "incongruent only", 4: "following congruent only",
                  5: "following incongruent only", 7: "left target only", 8: "right target only"}
        info.write(f"basic_filters, {','.join([ftypes[i] for i in data['filters']])}\n")
        # TODO - tidy this one
        info.write(f"extra_filters, {data['extra_filters']}\n")
        ttypes = {0: "none", 1: "to right", 2: "to left"}
        info.write(f"transformation, {ttypes[data['transformations']]}\n")
        ntypes = {0: "none", 1: "by subject", 2: "total"}
        info.write(f"normalisation, {ntypes[data['normalisation']]}\n")
        info.close()
    elif data["type"] == "quintile analysis":
        info = open(path+f"{data['label']}_info.csv", "w")
        info.write("subjects, " + ", ".join(sorted(data["subjects"])) + "\n")
        # for subject in data["subjects"]:
        info.write(f"n_bins, {data['n bins']}\n")
        info.write(f"sort_field, {data['sort field']}\n")
        for i in range(data["n bins"]):
            qr = data["q ranges"][i]
            info.write(f"bin_{i+1} range (max/min), {qr[0]}, {qr[1]}\n")
        ftypes = {1: "congruent only", 2: "incongruent only", 4: "following congruent only",
                  5: "following incongruent only", 7: "left target only", 8: "right target only"}
        info.write(f"basic_filters, {','.join([ftypes[i] for i in data['filters']])}\n")
        # TODO - tidy this one
        info.write(f"extra_filters, {data['extra_filters']}\n")
        ttypes = {0: "none", 1: "to right", 2: "to left"}
        info.write(f"transformation, {ttypes[data['transformations']]}\n")
        ntypes = {0: "none", 1: "by subject", 2: "total"}
        info.write(f"normalisation, {ntypes[data['normalisation']]}\n")
        info.close()

        def split_line(line):
            length = data["length"]
            bin_lines = []
            for i in range(len(data["subjects"])):
                j = i * length + i 
                bin_lines.append(line[j: j+length])
            return bin_lines

        df_pos = pd.DataFrame(index=list(range(1, data["length"]+1)))
        for i, bin_lines in enumerate(data["lines"]):
            lines = split_line(bin_lines)
            assign_dict = {}
            for j, line in enumerate(lines):
                # TODO TODO TODO CRITICAL make sure subject lines up with data
                assign_dict[f"subject_{data['subjects'][j]}_bin_{i+1}_pos_x"] = line[:, 0]
                assign_dict[f"subject_{data['subjects'][j]}_bin_{i+1}_pos_y"] = line[:, 2]
                assign_dict[f"subject_{data['subjects'][j]}_bin_{i+1}_pos_z"] = line[:, 1]
                df_pos = df_pos.assign(**assign_dict)

        df_pos.to_csv(path+f"{data['label']}_points.csv")


if __name__ == "__main__":
    rcsv = get_results()
    print(get_traj_data(rcsv, 1))
