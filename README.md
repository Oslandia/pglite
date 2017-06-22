# pglite

This a Python module allowing to use a PostgreSQL instance "as if" it was a simple SQLite database: no admin privileges, no configuration needed.

It manages a "local" PostgreSQL cluster in user's home (~/.pglite)

By default it opens a TCP port 55432 on localhost.

## Usage from the command line

This software installs a 'pglite' command line interface, with the following subcommands:

```
PGLite management tool. Commands:

init [path_to_pg_ctl]	Initialize the cluster
reset			Reset the cluster
status			Print the status of the cluster
start			Start the cluster
stop			Stop the cluster
create db_name		Create a database
drop db_name		Drop a database
list			List databases
export db_name file	Export a database to a dump file
import file db_name	Create a new database and import data from the dump file
psql			Launch a psql shell on the cluster
```

## Usage from another Python module

If you want to let your users the ability to transparently use a PostgreSQL dabatase without ever noticing it, call `pglite.init_cluster()` at some point (during install)
and then call `pglite.start_cluster()` at the beginning of your program (and possibly register `pglite.stop_cluster()` at the end with `atexit`). Then you can use
this "local" cluster with a connection on a local TCP port.

## Example

This example runs on Ubuntu 17.10, but you should be able to reproduce on various environments, including Windows.
First install the environment. You will need an existing PostgreSQL installation.
Then we install pglite and psycopg2 modules in a virtual Python environment.

```bash
sudo apt install postgresql-9.6
virtualenv playwithpg
. playwithpg/bin/activate
pip install pglite ipython psycopg2
```

Now run iPython and play :-)

```bash
ipython
```

```python
In [1]: import pglite
In [2]: import psycopg2
In [3]: pglite.init_cluster()
The files belonging to this database system will be owned by user "hme".
This user must also own the server process.

The database cluster will be initialized with locale "fr_FR.UTF-8".
The default text search configuration will be set to "french".

Data page checksums are disabled.

creating directory /home/hme/.pglite/pg_data ... ok
creating subdirectories ... ok
selecting default max_connections ... 100
selecting default shared_buffers ... 128MB
selecting dynamic shared memory implementation ... posix
creating configuration files ... ok
creating template1 database in /home/hme/.pglite/pg_data/base/1 ... ok
initializing pg_authid ... ok
initializing dependencies ... ok
creating system views ... ok
loading system objects' descriptions ... ok
creating collations ... ok
creating conversions ... ok
creating dictionaries ... ok
setting privileges on built-in objects ... ok
creating information schema ... ok
loading PL/pgSQL server-side language ... ok
vacuuming database template1 ... ok
copying template1 to template0 ... ok
copying template1 to postgres ... ok
syncing data to disk ... ok

WARNING: enabling "trust" authentication for local connections
You can change this by editing pg_hba.conf or using the option -A, or
--auth-local and --auth-host, the next time you run initdb.

Success. You can now start the database server using:

    /usr/lib/postgresql/9.5/bin/pg_ctl -D /home/hme/.pglite/pg_data -l logfile start

In [4]: pglite.start_cluster()
waiting for server to start.... done
server started

In [5]: con = psycopg2.connect(pglite.cluster_params() + " dbname=postgres")
In [6]: cur=con.cursor()
In [7]: cur.execute("""select version()""")
In [8]: rows = cur.fetchall()
In [9]: print rows
[('PostgreSQL 9.6.3 on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 6.3.0-12ubuntu2) 6.3.0 20170406, 64-bit',)]

In [10]: pglite.stop_cluster()
waiting for server to shut down.... done
server stopped
```
