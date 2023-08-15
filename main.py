import pandas as pd
import os
from DataReaders import read_activities_excel, get_file_list, read_json_data

my_excel = 'Samsung_Health_exports\com.samsung.shealth.exercise.20230813165934.csv'
jsons = 'Samsung_Health_exports\jsons\com.samsung.shealth.exercise'

main_df = read_activities_excel(my_excel)

file_db = get_file_list(jsons)
data_ids = pd.Series(file_db.index)

test_loc = file_db.index.get_loc('4ac7acfe-875c-4108-92a6-1c5ecc3fdaff')
test_path = file_db.iloc[test_loc, :]
read_json_data(test_path)

#
# for ids in data_ids:
#     test_loc = file_db.index.get_loc(ids)
#     test_path = file_db.iloc[test_loc, :]
#     print(ids)
#     read_json_data(test_path)


# test_path = pd.Series(file_db[file_db.index == '4ac7acfe-875c-4108-92a6-1c5ecc3fdaff'])
# read_json_data(test_path)
