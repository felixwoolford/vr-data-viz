from pathlib import Path
import os

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
        for s in os.listdir(Path(pp_data_path)):
            if os.path.isdir(Path(pp_data_path+s)):
                if keyword in s:
                    valid_sets.append(s)
        if not len(valid_sets):
            print(f"no {keyword} processed data for {subject}") 
            return None
        else:
            if len(valid_sets) > 1:
                print(f"too many {keyword} processed data for {subject}") 
            return valid_sets[0]
    except FileNotFoundError:
        print("invalid path found in data dir.")
        return None


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
    # TODO BROKEN for real version
    # global p_path
    # p_path = f"../data/VR-S1/Hand/{person}/S001/"
    # results_fname = p_path + "trial_results.csv"
    results_f = Path(results_fname).open()
    return pd.read_csv(results_f, delimiter=",", dtype=str).fillna("xx")


def get_subjects(base_path, all=False):
    if all:
        # TODO make this a dict with the traj location
        return sorted([s for s in os.listdir(Path(base_path)) 
                       if os.path.isdir(Path(base_path+s))])
    else:
        subjects = {}
        for s in os.listdir(Path(base_path)):
            path = base_path+s
            if os.path.isdir(Path(path)):
                pp_data_dir = get_processed_data_dir(s, path)
                if pp_data_dir is not None:
                    subjects[s] = f"{base_path}{s}/S001/{s}/{pp_data_dir}/"
        return subjects


def export_qa_data(data, output_fname):
    pass


if __name__ == "__main__":
    rcsv = get_results()
    print(get_traj_data(rcsv, 1))
