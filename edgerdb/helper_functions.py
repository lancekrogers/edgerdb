from .settings import settings as stg
from .db_loaders import *
from ftplib import FTP
import tempfile
import os
import zipfile
import datetime
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import socket
socket.setdefaulttimeout(240*60)


def db():
    connection = psycopg2.connect(
        dbname=stg.NEW_DBNAME,
        user=stg.NEW_USERNAME,
        host=stg.HOST,
        port=stg.PORT,
        password=stg.NEW_PASSWORD)
    return connection

def old_db():
    connection = psycopg2.connect(
    dbname=stg.DEFAULT_DBNAME,
    user=stg.DEFAULT_USER,
    password=stg.DEFAULT_PASSWORD,
    host=stg.HOST,
    port=stg.PORT,
    )
    return connection

def clear_sessions(dbname, connection):
    count = 0
    try:
        con = connection.cursor()
        con.execute("SELECT count(*) FROM pg_stat_activity;")
        count = int(con.fetchone()[0])
        con.execute("select pg_terminate_backend(pg_stat_activity.pid) from pg_stat_activity where pg_stat_activity.datname = '{}';".format(dbname))
        connection.close()
    except Exception as e:
        print(e)
    print("{} Sessions Cleared".format(count))


def statement(statement, connection, commit=False, close=True, output=True):
    cursor = connection.cursor()
    cursor.execute(statement)
    if output:
        output = cursor.fetchall()
        if commit == True:
            connection.commit()
        if close:
            connection.close()
        return output
    else:
        if commit == True:
            connection.commit()
        if close:
            connection.close()
        return [('Statement Executed',)]

def table_exist(tablename, connection):
    output = statement("select exists (select 1 from  pg_catalog.pg_class where relname = '{}');".format(tablename), connection)
    return output[0]

def create_or_replace_table(connection, tablename, column_string):
    con = connection
    cur = con.cursor()

    def table_check(cursor, tablename):
        query = "select exists (select 1 from  pg_catalog.pg_class where relname = '{}');".format(tablename)
        cursor.execute(query) # checking for table
        return cursor.fetchone()[0]

    if table_check(cur, tablename) == False:
        cur.execute("create table {} ({});".format(tablename, column_string))#"create table name (cik VARCHAR, conm VARCHAR, type VARCHAR, date VARCHAR, path VARCHAR);")
        con.commit()
    else:
        cur.execute("drop table {};".format(tablename))#"create table name (cik VARCHAR, conm VARCHAR, type VARCHAR, date VARCHAR, path VARCHAR);")
        con.commit()
        cur.execute("create table {} ({});".format(tablename, column_string))
        con.commit()
    con.close()
    return cur.statusmessage

def generate_daily_file_paths():
    ftp = FTP('ftp.sec.gov')
    ftp.login()
    d_index = ftp.nlst('edgar/daily-index')
    daily_files = [x for x in d_index if x.startswith('edgar/daily-index/master')]
    daily_files.sort()
    ftp.close()
    return daily_files

def generate_quarterly_file_paths():
    current_year = datetime.date.today().year
    current_quarter = (datetime.date.today().month - 1) // 3 + 1
    start_year = 1993
    years = list(range(start_year, current_year))
    quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
    history = [(y, q) for y in years for q in quarters]
    for i in range(1, current_quarter):
        history.append((current_year, 'QTR%d' % i))
    quarterly_files = ['edgar/full-index/%d/%s/master.zip' % (x[0], x[1]) for x
                       in history]
    quarterly_files.sort()
    return quarterly_files

def latest_index_in_db(tablename, connection):
    try:
        latest_file_in_db_query = 'select date from (select date, path  from {} order by date desc)as subquery limit 1;'.format(tablename)
        output = statement(latest_file_in_db_query, connection, close=True)
        return output[0]
    except:
        return None

# Use this function to load the latest daily files to the database
def load_latest_files(daily_files):
    tablename = "index_files"
    try:
        connection = db()
        latest_in_db = latest_index_in_db(tablename, connection)[0]
        connection.close()
    except:
        latest_in_db = 1
    for file in range(len(daily_files)):
        ddate = int(daily_files[file].split('.')[1])
        if latest_in_db < ddate:
            connection = db()
            load_daily_file(daily_files[file], connection, tablename)
            update_loaded_master_files(daily_files[file])
            update_log_table()
            connection.close()
        else:
            print("{} already loaded".format(daily_files[file]))
            continue

def update_loaded_master_files(file_path):
    timestamp = str(datetime.datetime.now())
    statement("""insert into loaded_master_files
                (path, timestamp) values ('{}', '{}') ;""".format(file_path, timestamp),db(), commit=True, close=True, output=False)

def update_log_table():
    timestamp = str(datetime.datetime.now())
    statement("update log_table set last_updated = '{}';".format(timestamp), db(), commit=True, close=True, output=False)

def load_daily_indices(daily_files, table_name):
    for file in daily_files:
        load_daily_file(file, db(), table_name)
        update_loaded_master_files(file)
        update_log_table()

def load_quarterly_files(q_files,table_name):
    for file in q_files:
        load_quarterly_file(file, db(), table_name)
        update_loaded_master_files(file)
        update_log_table()

def retrieve_document(file_path, directory='sec_filings'):
    '''
        This function takes a file path beginning with edgar and stores the form in a directory.
        The default directory is sec_filings but can be changed through a keyword argument.
    '''
    ftp = FTP('ftp.sec.gov', timeout=None)
    ftp.login()
    name = file_path.replace('/', '_')
    if not os.path.exists(directory):
        os.makedirs(directory)
    with tempfile.TemporaryFile() as temp:
        ftp.retrbinary('RETR %s' % file_path, temp.write)
        temp.seek(0)
        with open('{}/{}'.format(directory, name), 'w+') as f:
            f.write(temp.read().decode("utf-8"))
        f.closed
        records = temp
        retry = False
    ftp.close()
