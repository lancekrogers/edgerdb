from .helper_functions import *
from .settings import settings as stg
import datetime

def create_db_and_user():

    new_username = stg.NEW_USERNAME
    new_password = stg.NEW_PASSWORD
    new_db = stg.NEW_DBNAME

    if new_password != "":
        pass_phrase = "with password {}".format(new_password)
    else:
        pass_phrase = new_password
    try:
        connection_1 = old_db()
        statement("create user {} {} createdb createrole replication;".format(new_username, pass_phrase),
                  connection_1, commit=True, close=True, output=False)
        connection_1.close()
        print('User: {} created'.format(new_username))
    except Exception as e:
        print('User: {} already exist'.format(new_username))
    try:
        connection_2 = old_db()
        connection_2.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        statement("create database {};".format(new_db), connection_2, commit=False, close=True, output=False)
        print('Database {} created.'.format(new_db))
        connection_2.close()
    except Exception as e:
        print('Database {} already exist.'.format(new_db))


def initialize_database():
    timestamp = str(datetime.datetime.now())
    create_db_and_user()
    create_or_replace_table(db(),'index_files', '''cik INTEGER, company VARCHAR,
                                                    form_type VARCHAR, date INTEGER, path VARCHAR''')  # main table
    create_or_replace_table(db(), 'loaded_master_files', '''path VARCHAR, timestamp VARCHAR''')# loaded_master_files table
    create_or_replace_table(db(), 'log_table', 'last_updated VARCHAR, date_of_creation VARCHAR')# log table
    statement("""insert into log_table
                (last_updated, date_of_creation)
                values ('{}', '{}') ;""".format(timestamp, timestamp),db(), commit=True, close=True, output=False)


def delete_user_and_db():
    dbname = stg.NEW_DBNAME
    username = stg.NEW_USERNAME
    try:
        try:
            clear_sessions(dbname, db())
        except Exception as e:
            print('A problem occured clearing sessions for {}'.format(dbname))
        try:
            clear_sessions(stg.DEFAULT_DBNAME, old_db())
        except Exception as e:
            print('A problem occured clearing sessions for {}'.format(stg.DEFAULT_DBNAME))
    except Exception as e:
        print('Unable to clear sessions')
    try:
        connection_1 = old_db()
        connection_1.set_isolation_level(0)
        statement("drop database {};".format(dbname), connection_1, commit=True, close=True, output=False)
        connection_1.close()
        print('database {} deleted'.format(dbname))
    except Exception as e:
        print("database {} either can't be found or has been deleted".format(dbname))
    try:
        connection_2 = old_db()
        connection_2.set_isolation_level(0)
        statement("drop user {};".format(username), connection_2, commit=True, close=True, output=False)
        connection_2.close()
        print('user {} deleted'.format(username))
    except Exception as e:
        print("user {} either can't be found or has been deleted".format(username))
