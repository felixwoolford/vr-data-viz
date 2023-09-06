from pathlib import Path

import pandas as pd
# p_path = "../data/VR-S1/Hand/P01/S001/"
# results_fname = p_path + "trial_results.csv"


def get_traj_data(results_csv, trial_id, path):
    traj_field_name = "controllertracker_movement_location_0"
    traj_fname = results_csv[traj_field_name][trial_id]

    # filepath in data is incorrect and needs modifying
    traj_fname = "/".join(traj_fname.split("/")[-2:])
    traj_fname = path + traj_fname

    traj_f = Path(traj_fname).open()
    traj_csv = pd.read_csv(traj_f)
    traj_x = list(traj_csv["pos_x"])
    traj_y = list(traj_csv["pos_y"])
    traj_z = list(traj_csv["pos_z"])
    return (traj_x, traj_y, traj_z)


def get_results(results_fname):
    # TODO BROKEN for real version
    # global p_path
    # p_path = f"../data/VR-S1/Hand/{person}/S001/"
    # results_fname = p_path + "trial_results.csv"
    results_f = Path(results_fname).open()
    return pd.read_csv(results_f, delimiter=",")


if __name__ == "__main__":
    rcsv = get_results()
    print(get_traj_data(rcsv, 1))
