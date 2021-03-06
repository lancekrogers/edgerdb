# edgerdb


<p>This is a package that builds a local postgres database of SEC filings taken from ftp.sec.gov</p>


<p>This package can be pip installed into the desired directory:</p>

```pip install edgerdb```

<p>To create the database and insert the index files from ftp.sec.gov do the following:</p>


<pre>
from edgerdb import EdgerDb
edger = EdgerDb()
edger.create_and_load()</pre>




<p>This installs a database with three tables.</p>
<ul>
  <li>filings</li>
  <li>loaded_master_files</li>
  <li>last_updated</li>
</ul>
<p>filings is the table that will contain information on all the SEC filings.</p>
<p>loaded_master_files contains a list of all the files currently loaded into the filings table</p>
<p>last_updated has the time that the last file was loaded into the database</p><br />
<p> To remove the database and user run: </p>


<pre>edger.delete_everything()</pre>


<p>Some functions are built in and can be used by importing helper_functions:</p>

<br />

<pre>
from edgerdb import helper_functions as hlp
</pre>

<p>The most used functions will be db(), old_db(), statement(), clear_sessions() and retrieve_document().</p>
<p>db() is used to create a open a connection object with the postgres database.</p>
<p> It is important to close the connection after every operation is performed.</p><br />

<pre>
con = hlp.db()

con.close()
</pre>

<p>statement() is used to run SQL queries on the database. statement() takes in the sql query as a string, a connection object and has optional keyword arguments. If close defaults to True to automatically close the connection after the query is run.</p>

<pre>
  statement(statement, connection, commit=False, close=True, output=True)

</pre>

<p>Ex:</p>

<pre>
top_five_paths = hlp.statement("select path from filings limit 5;", hlp.db(), close=True)
</pre>

<p>
retrieve_document() requires a path to file from filings table.  It takes this as input and downloads a copy of the file from edgar and stores it in a "sec_filings" directory in the same directory as your project. This can be changed with the optional directory keyword argument.
</p>
<p>Ex:</p>
<pre>
for path in top_five_paths:
    hlp.retrieve_document(path)
</pre>

<p>clear_sessions() can be used to clear running sessions on either the sec database or the main postgres database. The function requires two arguments.</p>
<pre>
clear_sessions(dbname, connection)
</pre>
<p>dbname is the name of the database and connection is a connection object. To clear sessions on the edgar database use db() and for the generic database use old_db().</p>
<p>Ex:</p>
<pre>
hlp.clear_sessions('edgar', hlp.db())
</pre>

<pre>
hlp.clear_sessions('edgar', old_db())
</pre>
<p> The database can easily be updated by providing the last date from the files in the database and
    the list of daily_files
</p>
<p>Ex:</p>
<pre>
from edgerdb import helper_functions as hlp

daily_files = hlp.generate_daily_file_paths()

last_date_in_db = int(hlp.latest_index_in_db('filings', hlp.db())[0])

hlp.load_latest_files(daily_files, last_date=last_date_in_db)
</pre>
<p> dir() can be used to explore the other functions that come with helper_functions </p>

<pre>
dir(hlp)
</pre>
