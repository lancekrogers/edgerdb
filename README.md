# edgerdb


<p>This is a package that builds a local postgres database of SEC filings taken from ftp.sec.gov</p>


<p>This package can be pip installed into the desired direcory:</p>

```pip install edgerdb```

<p>To create the database and insert the index files from ftp.sec.gov do the following:</p>

```from edgerdb import EdgerDb``` <br />
```edger = EdgerDb()```<br />
```edger.create_and_load()``` <br />

<p>This installs a database with three tables.</p>
<ul>
  <li>index_files</li>
  <li>loaded_master_files</li>
  <li>last_updated</li>
</ul>
<p>index_files is the table that will contain information on all the SEC filings.</p>
<p>loaded_master_files contains a list of all the files currently loaded into the index_files table</p>
<p>last_updated has the time that the last file was loaded into the database</p><br />
<p> To remove the database and user run: </p>
```edger.delete_everything()```<br />


