from .helper_functions import *

def load_daily_file(file_path, connection, tablename):
    dlog_file = open("edgerdb/logs/daily.log", "a")
    ftp = FTP('ftp.sec.gov', timeout=None)
    ftp.login()
    cursor = connection.cursor()
    cursor.execute("select column_name from information_schema.columns where table_name='{}';".format(tablename))
    fetch_columns = cursor.fetchall()
    columns = ""
    for val in fetch_columns:
        columns = columns + val[0]
        if fetch_columns[-1] == val:
            break
        columns = columns + ", "
    retry = True
    count = 0
    while retry:
        try:
            count += 1
            with tempfile.TemporaryFile() as temp:
                ftp.retrbinary('RETR %s' % file_path, temp.write)
                temp.seek(0)
                for x in range(7):
                    temp.readline()
                records = [tuple(line.decode('latin-1').rstrip().split('|')) for line in temp]
                retry = False
                print("Successful binary retrieveal on try # {} for {}".format(count, file_path))
        except Exception as e:
            print("Failed to retrieve binary on try # {} for {}".format(count, file_path), file=dlog_file)
            if count > 10:
                raise e
            print("Retrying...", file=dlog_file)
            retry = True
    clean_records = []
    for record in records:
        for i in range(len(record)):
            record[i] = re.sub("[']", "", record[i])
        clean_records.append(tuple(record))
    insert_t = "INSERT INTO {}({}) VALUES".format(tablename, columns)
    statements = [insert_t + '{}'.format(x) for x in clean_records]
    for state in statements:
        try:
            cursor.execute(state)
            connection.commit()
        except:
            continue
    print(cursor.statusmessage, file=dllog_file)
    connection.close()
    ftp.close()
    dlog_file.close()
    return cursor.statusmessage


def load_quarterly_file(file_path, connection, tablename):
    log_file = open("edgerdb/logs/quarterly.log", "a")
    ftp = FTP('ftp.sec.gov', timeout=None)
    ftp.login()
    cursor = connection.cursor()
    cursor.execute("select column_name from information_schema.columns where table_name='{}';".format(tablename))
    fetch_columns = cursor.fetchall()
    columns = ""
    for val in fetch_columns:
        columns = columns + val[0]
        if fetch_columns[-1] == val:
            break
        columns = columns + ", "
    retry = True
    count = 0
    while retry:
        try:
            count += 1
            with tempfile.TemporaryFile() as temp:
                ftp.retrbinary('RETR %s' % file_path, temp.write)
                with zipfile.ZipFile(temp).open('master.idx') as z:
                    for i in range(10):
                        z.readline()
                    records = [line.decode('latin-1').rstrip().split('|') for line in z]
                retry = False
                print("Successfull Binary Retrieval on try # {} for {}".format(count, file_path), file=log_file)
        except Exception as e:
            print("Failure to retrieve binary on try # {} for {}".format(count, file_path), file=log_file)
            if count > 10:
                raise e
            print(e, file=log_file)
            print("Retrying...", file=log_file)

            retry = True
    clean_records = []
    for record in records:
        for i in range(len(record)):
            record[i] = re.sub("[']", "", record[i])
            if i == 3:
                record[3] = record[i].replace('-', '')
        clean_records.append(tuple(record))
    insert_t = "INSERT INTO {}({}) VALUES".format(tablename, columns)
    statements = [insert_t + '{}'.format(x) for x in clean_records]
    for state in statements:
        try:
            cursor.execute(state)
            connection.commit()
        except Exception as e:
            print('Error in {}'.format(state), file=log_file)
            print('\n' + str(e) + "\n", file=log_file)
            continue

    connection.close()
    ftp.close()
    print(cursor.statusmessage, file=log_file)
    log_file.close()
    return cursor.statusmessage
