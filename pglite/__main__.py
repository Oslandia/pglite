from .pglite import check_cluster, init_cluster, reset_cluster, start_cluster, stop_cluster, cluster_params, is_started, create_db, drop_db, list_db, export_db, import_db, die, psql
import sys

usage = """
    usage pglite <command> [arguments]

    PGLite management tool. 
    
    Commands:\n
    
    init [path_to_pg_ctl]   Initialize the cluster

    reset                   Reset the cluster

    status                  Print the status of the cluster

    start                   Start the cluster

    stop [mode]             Stop the cluster (mode=smart|fast|immediate)

    create db_name          Create a database

    drop db_name            Drop a database

    list                    List databases

    export db_name file     Export a database to a dump file

    import file db_name     Create a new database and import data from the dump file

    psql                    Launch a psql shell on the cluster
    """

if len(sys.argv) < 2 or sys.argv[1] == '--help' or sys.argv[1] == 'help' or sys.argv[1] == '-h':
    print(usage)
    exit(0)

if sys.argv[1] == "init":
    pg_ctl_path = None
    if len(sys.argv) > 2:
        pg_ctl_path = sys.argv[2]
    init_cluster(pg_ctl_path)
elif sys.argv[1] == "reset":
    reset_cluster()
elif sys.argv[1] == "status":
    print_cluster_status()
elif sys.argv[1] == "start":
    check_cluster() or die("Cluster not present")
    start_cluster()
elif sys.argv[1] == "stop":
    shutdown_mode = "fast"
    if len(sys.argv) > 2:
        shutdown_mode = sys.argv[2]
    check_cluster() or die("Cluster not present")
    stop_cluster(shutdown_mode)
elif sys.argv[1] == "list":
    check_cluster() or die("Cluster not present")
    print("\n".join(list_db()))
elif sys.argv[1] == "create":
    check_cluster() or die("Cluster not present")
    if len(sys.argv) < 3:
        raise RuntimeError("Needed argument: db name")
    create_db(sys.argv[2])
elif sys.argv[1] == "drop":
    check_cluster() or die("Cluster not present")
    if len(sys.argv) < 3:
        raise RuntimeError("Needed argument: db name")
    drop_db(sys.argv[2])
elif sys.argv[1] == "export":
    check_cluster() or die("Cluster not present")
    if len(sys.argv) < 4:
        raise RuntimeError("Needed arguments: db_name dump_file")
    export_db(sys.argv[2], sys.argv[3])
elif sys.argv[1] == "import":
    check_cluster() or die("Cluster not present")
    if len(sys.argv) < 4:
        raise RuntimeError("Needed arguments: dump_file db_name")
    import_db(sys.argv[2], sys.argv[3])
elif sys.argv[1] == "psql":
    check_cluster() or die("Cluster not present")
    psql(sys.argv[2:])
else:
    print(usage)
    exit(1)

