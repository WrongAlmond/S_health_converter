import pandas as pd
from DataReaders import read_activities_excel, get_file_list, read_json_for_tcx, get_tcx_header_data, \
                        create_tcx_header, create_tcx_track_points, create_tcx_footer, save_tcx

my_excel = 'Samsung_Health_exports\com.samsung.shealth.exercise.20230813165934.csv'
jsons = 'Samsung_Health_exports\jsons\com.samsung.shealth.exercise'

# reading main csv containing summary of exercise data
main_df = read_activities_excel(my_excel)

# getting list of json files containing exercise info
file_db = get_file_list(jsons)


# #### Start of working stuff
#
# test_id = '4ac7acfe-875c-4108-92a6-1c5ecc3fdaff'
#
# # reading json for selected ID
# json_data = read_json_for_tcx(file_db, test_id)
#
# # reading data for creating tcx header
# header_data = get_tcx_header_data(main_df, test_id)
#
# # creating tcx
# header = create_tcx_header(header_data)
# body = create_tcx_track_points(json_data)
# footer = create_tcx_footer(header_data)
# save_tcx(header, body, footer, header_data[0], test_id)
#
# ## end of working stuff
#
#
# data_ids = pd.Series(file_db.index)
# failed_files = []
# for i in range(0, len(data_ids)):
#     # reading json for selected ID
#     json_data = read_json_for_tcx(file_db, data_ids[i])
#
#     # reading data for creating tcx header
#     header_data = get_tcx_header_data(main_df, data_ids[i])
#     if header_data:
#         # creating tcx
#         header = create_tcx_header(header_data)
#         body = create_tcx_track_points(json_data)
#         footer = create_tcx_footer(header_data)
#         save_tcx(header, body, footer, header_data[0], data_ids[i])
#
#         print(f"progress: {round(i/len(data_ids),4)*100}%")
#     else:
#         print(f"no info found for {data_ids[i]} in main csv")
#         failed_files.append(data_ids[i])


#### Start of working stuff 2

test_id = 'd81b1b76-bcad-409f-a1e3-f4f953d01a78'

# reading json for selected ID
json_data = read_json_for_tcx(file_db, test_id)

# reading data for creating tcx header
header_data = get_tcx_header_data(main_df, test_id)

if header_data:
    # creating tcx
    header = create_tcx_header(header_data)
    body = create_tcx_track_points(json_data)
    footer = create_tcx_footer(header_data)
    save_tcx(header, body, footer, header_data[0], test_id)


## end of working stuff
