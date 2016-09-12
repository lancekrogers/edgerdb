from .helper_functions import generate_daily_file_paths, generate_quarterly_file_paths
from .initialize_db import create_db_and_user, delete_user_and_db, initialize_database
from .populate import populate_database


class EdgerDb:

    def __init__(self):
        self.daily_files = generate_daily_file_paths()
        self.quarterly_files = generate_quarterly_file_paths()

    def create_and_load(self):
        """
            Use this to create a user, a database, and load the database with files.
            It will take a while to run and will only work if your network allows FTP
            file transfer.  It also requires you to have a postgres server running locally.
        """
        create_db_and_user()
        initialize_database()
        populate_database(self.daily_files, self.quarterly_files)

    def delete_everything(self):
        delete_user_and_db()
