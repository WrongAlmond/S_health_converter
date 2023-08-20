import pandas as pd
import os


def read_activities_excel(file_name):
    data_frame = pd.read_csv(file_name, skiprows=1, index_col=False)

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

    data_frame["com.samsung.health.exercise.exercise_type"].replace(sport_types, inplace=True)
    data_frame.index = data_frame['com.samsung.health.exercise.datauuid']

    return data_frame


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


def read_json_for_tcx(file_db, test_id):
    test_loc = file_db.index.get_loc(test_id)
    path = file_db.iloc[test_loc, :]

    used_files = ["com.samsung.health.exercise.live_data.json",
                  "com.samsung.health.exercise.location_data.json",
                  "live_data_internal.json",
                  "location_data_internal.json"]

    compiled_frame = pd.read_json(path[used_files[0]])

    for i in range(1, len(used_files)):
        path_to_read = path[used_files[i]]
        if not (pd.isna(path_to_read)):
            my_json = pd.read_json(path_to_read)
            compiled_frame = pd.merge(compiled_frame, my_json, on="start_time", how="outer")

    compiled_frame.sort_values(by="start_time", inplace=True)

    columns_to_drop = ['percent_of_vo2max', 'accuracy', 'elapsed_time_x',
                       'interval_x', 'segment_x', 'elapsed_time_y',
                       'interval_y', 'segment_y']

    for col in compiled_frame:
        if col in columns_to_drop:
            compiled_frame.drop([col], axis='columns', inplace=True)

    # compiled_frame = compiled_frame.resample("2S", on='start_time').mean()
    #
    # compiled_frame['start_time'] = compiled_frame.index
    # compiled_frame.to_csv("test.csv")

    return compiled_frame


def get_tcx_header_data(df, data_id):
    if data_id in df.index:
        row_id = df.index.get_loc(data_id)
        row_data = df.iloc[row_id, :]

        # header data
        sport_type = row_data['com.samsung.health.exercise.exercise_type']
        start_time = row_data['com.samsung.health.exercise.start_time']
        total_time_sec = row_data['com.samsung.health.exercise.duration'] / 1000  # original data in ms
        distance_meters = row_data['com.samsung.health.exercise.distance']
        max_speed = row_data['com.samsung.health.exercise.max_speed']
        calories = row_data['com.samsung.health.exercise.calorie']
        max_hr = row_data['com.samsung.health.exercise.max_heart_rate']
        mean_hr = row_data['com.samsung.health.exercise.mean_heart_rate']
        mean_cadence = row_data['com.samsung.health.exercise.mean_cadence']
        max_cadence = row_data['com.samsung.health.exercise.max_cadence']
        mean_speed = row_data['com.samsung.health.exercise.mean_speed']

        header_data = [sport_type, start_time, total_time_sec, distance_meters, max_speed, calories, max_hr, mean_hr,
                       mean_cadence, max_cadence, mean_speed]

        # for i in range(len(header_data)):
        #     if pd.isna(header_data[i]):
        #         header_data[i] = 0
        #         print("NAN FOUND")

        return header_data
    else:
        return False


def create_tcx_header(header_data):
    #  header_data = [sport_type, start_time, total_time_sec, distance_meters, max_speed, calories, max_hr, mean_hr,
    #                    mean_cadence, max_cadence]
    header_data[1] = f"{header_data[1].replace(' ', 'T')}"
    header = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<TrainingCenterDatabase\n'
        f'  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"\n'
        f'  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"\n'
        f'  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"\n'
        f'  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"\n'
        f'  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"\n'
        f'  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">\n'
        f'  <Activities>\n'
        f'    <Activity Sport="{header_data[0]}">\n'
        f'      <Id>{header_data[1]}Z</Id>\n'
        f'      <Lap StartTime="{header_data[1]}Z">\n'

    )

    if not (pd.isna(header_data[2])):
        header += (
            f'        <TotalTimeSeconds>{header_data[2]}</TotalTimeSeconds>\n')

    if not (pd.isna(header_data[3])):
        header += (
            f'        <DistanceMeters>{header_data[3]}</DistanceMeters>\n')

    if not (pd.isna(header_data[4])):
        header += (
            f'        <MaximumSpeed>{header_data[4]}</MaximumSpeed>\n')

    if not (pd.isna(header_data[5])):
        header += (
            f'        <Calories>{int(header_data[5])}</Calories>\n')

    if not (pd.isna(header_data[7])):
        header += (
            f'        <AverageHeartRateBpm>\n'
            f'          <Value>{int(header_data[7])}</Value>\n'
            f'        </AverageHeartRateBpm>\n')

    if not (pd.isna(header_data[6])):
        header += (
            f'        <MaximumHeartRateBpm>\n'
            f'          <Value>{int(header_data[6])}</Value>\n'
            f'        </MaximumHeartRateBpm>\n')

    header += (
        f'        <Intensity>Active</Intensity>\n'
        f'        <TriggerMethod>Manual</TriggerMethod>\n')

    return header


def create_tcx_track_points(input_track_points):
    # ['heart_rate', 'start_time', 'cadence', 'distance', 'speed', 'altitude', 'latitude', 'longitude', 'cadence']
    cols = input_track_points.columns

    if len(input_track_points) > 0:
        data_out = f"        <Track>\n"
        distance = 0.0

        for index, row in input_track_points.iterrows():
            time_stamp = f"{str(row['start_time']).replace(' ', 'T')}Z"

            data_out += f"          <Trackpoint>\n"
            data_out += (
                f"            <Time>{time_stamp}</Time>\n"
            )

            if "latitude" in cols and "longitude" in cols:
                if not (pd.isna(row["latitude"])) and not (pd.isna(row["longitude"])):
                    data_out += (
                        f"            <Position>\n"
                        f"              <LatitudeDegrees>{row['latitude']}</LatitudeDegrees>\n"
                        f"              <LongitudeDegrees>{row['longitude']}</LongitudeDegrees>\n"
                        f"            </Position>\n"
                    )

            if "altitude" in cols:
                if not (pd.isna(row["altitude"])):
                    data_out += (
                        f"            <AltitudeMeters>{row['altitude']}</AltitudeMeters>\n"
                    )

            if "distance" in cols:
                if not (pd.isna(row["distance"])):
                    distance += row['distance']
                    data_out += (
                        f"            <DistanceMeters>{distance}</DistanceMeters>\n"
                    )

            if "heart_rate" in cols:
                if not (pd.isna(row["heart_rate"])):
                    data_out += (
                        f"            <HeartRateBpm>\n"
                        f"              <Value>{int(row['heart_rate'])}</Value>\n"
                        f"            </HeartRateBpm>\n"
                    )

            if "speed" in cols and 'cadence' in cols:
                if not (pd.isna(row["speed"])) and not (pd.isna(row["cadence"])):
                    data_out += (
                        f"            <Extensions>\n"
                        f"              <ns3:TPX>\n"
                        f"                <ns3:Speed>{row['speed']}</ns3:Speed>\n"
                        f"                <ns3:RunCadence>{row['cadence']}</ns3:RunCadence>\n"
                        f"              </ns3:TPX>\n"
                        f"            </Extensions>\n"
                    )
            elif "speed" in cols:
                if not (pd.isna(row["speed"])):
                    data_out += (
                        f"            <Extensions>\n"
                        f"              <ns3:TPX>\n"
                        f"                <ns3:Speed>{row['speed']}</ns3:Speed>\n"
                        f"              </ns3:TPX>\n"
                        f"            </Extensions>\n"
                    )

            elif "cadence" in cols:
                if not (pd.isna(row["cadence"])):
                    data_out += (
                        f"            <Extensions>\n"
                        f"              <ns3:TPX>\n"
                        f"                <ns3:RunCadence>{row['cadence']}</ns3:RunCadence>\n"
                        f"              </ns3:TPX>\n"
                        f"            </Extensions>\n"
                    )

            data_out += f"          </Trackpoint>\n"
        data_out += f"        </Track>\n"

        return data_out


def create_tcx_footer(header_data):
    # header_data = [sport_type, start_time, total_time_sec, distance_meters, max_speed, calories, max_hr, mean_hr,
    #                mean_cadence, max_cadence, mean_speed]
    footer_data = ""

    if not (pd.isna(header_data[10])) or not (pd.isna(header_data[8])) or not (pd.isna(header_data[9])):
        footer_data += (
            f"    <Extensions>\n"
            f"      <ns3:LX>\n")
    if not (pd.isna(header_data[10])):
        footer_data += (
            f"        <ns3:AvgSpeed>{header_data[10]}</ns3:AvgSpeed>\n")
    if not (pd.isna(header_data[8])):
        footer_data += (
            f"        <ns3:AvgRunCadence>{header_data[8]}</ns3:AvgRunCadence>\n")
    if not (pd.isna(header_data[9])):
        footer_data += (
            f"        <ns3:MaxRunCadence>{header_data[9]}</ns3:MaxRunCadence>\n")
    if not (pd.isna(header_data[10])) or not (pd.isna(header_data[8])) or not (pd.isna(header_data[9])):
        footer_data += (
            f"      </ns3:LX>\n"
            f"    </Extensions>\n")

    footer_data += (
        f"    </Lap>\n"
        f'    <Creator xsi:type="Device_t">\n'
        f"      <Name> Samsung Galaxy Watch</Name>\n"
        f"      <UnitId>0000000000</UnitId>\n"
        f"      <ProductID>0000</ProductID>\n"
        f"      <Version>\n"
        f"        <VersionMajor>0</VersionMajor>\n"
        f"        <VersionMinor> 0 </VersionMinor>\n"
        f"        <BuildMajor>0</BuildMajor>\n"
        f"        <BuildMinor>0</BuildMinor>\n"
        f"      </Version>\n"
        f"    </Creator>\n"
        f"  </Activity>\n"
        f"</Activities>\n"
        f'<Author xsi:type="Application_t">\n'
        f"  <Name>Connect Api</Name>\n"
        f"  <Build>\n"
        f"    <Version>\n"
        f"      <VersionMajor>0</VersionMajor>\n"
        f"      <VersionMinor>0</VersionMinor>\n"
        f"      <BuildMajor>0</BuildMajor>\n"
        f"      <BuildMinor>0</BuildMinor>\n"
        f"    </Version>\n"
        f"  </Build>\n"
        f"  <LangID>en</LangID>\n"
        f"  <PartNumber>000-00000-00</PartNumber>\n"
        f"</Author>\n"
        f"</TrainingCenterDatabase>\n")

    return footer_data


def save_tcx(header, json_data, footer, activity, id_no):
    data = header + json_data + footer
    with open(f'data_exports/{activity}_{id_no}.tcx', 'w+') as f:
        f.write(data)
