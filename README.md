pglite
======

This a Python module allowing to use a PostgreSQL instance "as if" it was a simple SQLite database: no admin privileges, no configuration needed.

It manages a "local" PostgreSQL cluster in user's home (~/.pglite)

Usage from the command line
------

This installs a 'pglite' command line interface, with the following subcommands:

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

Usage from another Python module
----

If you want to let your users the ability to transparently use a PostgreSQL dabatase without ever noticing it, call `pglite.init_cluster()` at some point (during install)
and then call `pglite.start_cluster()` at the beginning of your program (and possibly register `pglite.stop_cluster()` at the end with `atexit`). Then you can use
this "local" cluster with a connection on a local TCP port.
