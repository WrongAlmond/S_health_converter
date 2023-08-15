import pandas as pd
import os


def read_activities_excel(file_name):
    raw_data_frame = pd.read_csv(file_name, skiprows=1, index_col=False)

    col_select = ["live_data_internal",
                  "total_calorie",
                  "location_data_internal",
                  "additional_internal",
                  "com.samsung.health.exercise.duration",
                  "com.samsung.health.exercise.location_data",
                  "com.samsung.health.exercise.start_time",
                  "com.samsung.health.exercise.exercise_type",
                  "com.samsung.health.exercise.mean_heart_rate",
                  "com.samsung.health.exercise.max_heart_rate",
                  "com.samsung.health.exercise.create_time",
                  "com.samsung.health.exercise.max_speed",
                  "com.samsung.health.exercise.mean_cadence",
                  "com.samsung.health.exercise.min_heart_rate",
                  "com.samsung.health.exercise.distance",
                  "com.samsung.health.exercise.calorie",
                  "com.samsung.health.exercise.max_cadence",
                  "com.samsung.health.exercise.vo2_max",
                  "com.samsung.health.exercise.live_data",
                  "com.samsung.health.exercise.mean_speed",
                  "com.samsung.health.exercise.end_time",
                  "com.samsung.health.exercise.datauuid",
                  "com.samsung.health.exercise.sweat_loss"]

    select_data = raw_data_frame[col_select].copy()

    sport_types = {1001: "Walking",
                   11007: "Cycling",
                   1002: "Running",
                   0: "Other",
                   14001: "Swimming",
                   10007: "Gym",
                   13001: "Hiking",
                   15005: "Treadmill",
                   15004: "Rowing_machine",
                   15002: "Garmin_breathing_exc",
                   13002: "Rock_climbing"}

    select_data["com.samsung.health.exercise.exercise_type"].replace(sport_types, inplace=True)

    for col in select_data.columns:
        select_data.rename(columns={col: col.replace("com.samsung.health.exercise.", "")}, inplace=True)

    return select_data


def get_file_list(path):
    # we shall store all the file names in this list
    filelist = []

    for root, dirs, files in os.walk(path):
        for file in files:
            # append the file name to the list
            filelist.append(os.path.join(root, file))

    file_dicts = {}
    file_types = []
    for file in filelist:
        data_id = str(file.split('\\')[-1]).split('.')[0]
        file_type = str(file.split('\\')[-1]).replace(f"{data_id}.", "")
        file_types.append(file_type)

        if data_id in file_dicts:

            file_dicts[data_id][file_type] = file

        else:
            file_dicts[data_id] = {file_type: file}

    return pd.DataFrame(file_dicts).transpose()


def read_json_data(path):
    accepted_files = ["com.samsung.health.exercise.live_data.json",
                      "com.samsung.health.exercise.location_data.json",
                      "live_data_internal.json",
                      "location_data_internal.json"]

    compiled_frame = pd.read_json(path[accepted_files[0]])
    # print(compiled_frame.columns)

    # for file in path:
    #     # if not(pd.isna(file)) and "com.samsung.health.exercise.live_data.json" not in str(file) and "live" in str(file) and "location" in str(file):
    #     if not (pd.isna(file)) and "com.samsung.health.exercise.live_data.json" not in str(file):
    for i in range(1, len(accepted_files)):
        path_to_read = path[accepted_files[i]]
        if not(pd.isna(path_to_read)):
            my_json = pd.read_json(path_to_read)
            compiled_frame = pd.merge(compiled_frame, my_json, on="start_time", how="outer")

    compiled_frame.sort_values(by="start_time", inplace=True)

    # compiled_frame.to_csv("test.csv")

    # raw_data = pd.read_json(path)
    # print((raw_data))
    return compiled_frame
