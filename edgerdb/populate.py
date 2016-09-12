from .db_loaders import *
from .helper_functions import load_daily_indices, statement, load_quarterly_files, db

def populate_database(daily_files, quarterly_files):
    d_files = daily_files
    q_files = quarterly_files
    tablename = "index_files"
    try:
        loaded_files =[x[0] for x in statement("select path from loaded_master_files;", db())]
    except Exception as e:
        loaded_files = []
        print(e)

    def remove_already_loaded_files(input_files, loaded_master_files):
        short_list = input_files
        for file in short_list:
            if file in loaded_master_files:
                try:
                    short_list.remove(file)
                except:
                    continue
        return short_list

    def quarterly_file_continuation(quarterly_files, last_year):
        q_files = quarterly_files
        matrix = []
        for x in q_files:
            n = x.split('/')
            matrix.append(n)
        files_left = []
        for x in range(len(q_files)):
            year = int(matrix[x][2])
            if year > last_year:
                files_left.append(q_files[x])
        return files_left

    quarterly_files = remove_already_loaded_files(q_files, loaded_files)
    daily_files = remove_already_loaded_files(d_files, loaded_files)
    try:
        load_quarterly_files(quarterly_files, tablename)
    except Exception as e:
        print(e)
        try:
            lr_select_statement = """select * from (select cast(substr( cast (date as text), 1, 4) as integer) from
            {} order by date desc) as foo limit 1;""".format(tablename)
            last_year = statement(lr_select_statement, db())
            if last_year:
                continuation = quarterly_file_continuation(quarterly_files, last_year[0][0])
                load_quarterly_files(continuation, tablename)
        except Exception as e:
            print("Quarterly Files Failed to load")
            print(e)
    load_daily_indices(daily_files, tablename)
