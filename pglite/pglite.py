#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import os
import sys
import ConfigParser
import subprocess

# base directory
PGLITE_DB_DIR = os.path.join(os.path.expanduser("~"), ".pglite")
# configuration file
PGLITE_DB_CONF = os.path.join(PGLITE_DB_DIR, "db.conf")
# directory where Postgresql data are written
PGLITE_DB_PGDATA = os.path.join(PGLITE_DB_DIR, "pg_data")
# don't export tables in _tempus_import
PGLITE_EXTRA_DUMP_OPTIONS = ["-N", "_tempus_import"]
PGLITE_DEFAULT_PORT = 55432

def die(msg):
    raise RuntimeError(msg)

def write_config(c_dict):
    c = ConfigParser.ConfigParser()
    c.add_section("cluster")
    for k, v in c_dict.items():
        c.set("cluster", k, v)
    with open(PGLITE_DB_CONF, 'wb') as configfile:
        c.write(configfile)

def read_config():
    c = ConfigParser.ConfigParser()
    c.read(PGLITE_DB_CONF)
    return dict(c.items("cluster"))

def check_cluster():
    """Check if db exists"""
    return os.path.isdir(PGLITE_DB_DIR) and os.path.isfile(PGLITE_DB_CONF) and os.path.isdir(PGLITE_DB_PGDATA)

def find_pg_ctl():
    """Find the pg_ctl executable in common places"""
    if sys.platform.startswith('linux'):
        paths = ['/usr/lib/postgresql/9.6/bin/pg_ctl',
                 '/usr/lib/postgresql/9.5/bin/pg_ctl',
                 '/usr/lib/postgresql/9.4/bin/pg_ctl',
                 '/usr/lib/postgresql/9.3/bin/pg_ctl']
    else: # Windows
        paths = [ os.path.join(os.environ["OSGEO4W_ROOT"], "bin", "pg_ctl.exe"),
                  os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "9.6", "bin", "pg_ctl.exe"),
                 os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "9.5", "bin", "pg_ctl.exe"),
                 os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "9.4", "bin", "pg_ctl.exe")]
    for p in paths:
        if os.path.isfile(p):
            print("Found pg_ctl at " + p)
            return p
    return None

def init_cluster(pg_ctl_path=None):
    """
    Initialize a db directory
    @param pg_ctl_path the path to the pg_ctl executable. If None, it will be looked for
    """
    if check_cluster():
        # nothing to do
        print("Cluster already present")
        return
    if pg_ctl_path is None:
        pg_ctl_path = find_pg_ctl() or die("Can't find pg_ctl")
    subprocess.Popen([pg_ctl_path, "init", "-D", PGLITE_DB_PGDATA, "-s"]).communicate()

    # modify postgresql.conf (append some lines)
    port = PGLITE_DEFAULT_PORT
    with open(os.path.join(PGLITE_DB_PGDATA, "postgresql.conf"), "a") as f:
        f.write("port={}\n".format(port))
        f.write("unix_socket_directories='{}'\n".format(PGLITE_DB_DIR))

    # write the config file
    write_config({'pg_ctl_path': pg_ctl_path, 'port': port})

def reset_cluster():
    """Remove a DB cluster"""
    if not check_cluster():
        # nothing to do
        return
    stop_cluster()
    import shutil
    shutil.rmtree(PGLITE_DB_DIR)

def start_cluster():
    if is_started():
        # nothing to do
        return
    c = read_config()
    subprocess.Popen([c['pg_ctl_path'], "start", "-w", "-D", PGLITE_DB_PGDATA, "-l", os.path.join(PGLITE_DB_DIR, "postgresql.log")]).communicate()

def stop_cluster():
    if not is_started():
        # nothing to do
        print("DB already stopped")
        return
    c = read_config()
    subprocess.Popen([c['pg_ctl_path'], "stop", "-D", PGLITE_DB_PGDATA]).communicate()

def cluster_params():
    c = read_config()
    return "host=localhost port={}".format(c['port'])

def is_started():
    c = read_config()
    out, err = subprocess.Popen([c['pg_ctl_path'], "status", "-D", PGLITE_DB_PGDATA], stdout=subprocess.PIPE).communicate()
    return out.find("PID") != -1

def create_db(db_name):
    start_cluster()
    c = read_config()
    subprocess.Popen([os.path.join(os.path.dirname(c['pg_ctl_path']), "createdb"), "-h", "localhost", "-p", c['port'], db_name]).communicate()

def drop_db(db_name):
    start_cluster()
    c = read_config()
    subprocess.Popen([os.path.join(os.path.dirname(c['pg_ctl_path']), "dropdb"), "-h", "localhost", "-p", c['port'], db_name]).communicate()

def list_db():
    start_cluster()
    c = read_config()
    sql = "select datname from pg_database where datname not in ('template0', 'template1', 'postgres')"
    out, err = subprocess.Popen([os.path.join(os.path.dirname(c['pg_ctl_path']), "psql"), "-h", "localhost", "-p", c['port'], "postgres", "-t", "-c", sql], stdout = subprocess.PIPE).communicate()
    return [x.strip() for x in out.split('\n')[:-2]]

def export_db(db_name, dump_file):
    start_cluster()
    import zlib
    zc = zlib.compressobj()
    c = read_config()
    a = [os.path.join(os.path.dirname(c['pg_ctl_path']), "pg_dump"), "-h", "localhost", "-p", c['port'], db_name, "-O", "-x"]
    a += PGLITE_EXTRA_DUMP_OPTIONS
    p = subprocess.Popen(a, stdout = subprocess.PIPE)
    with open(dump_file, "wb") as fo:
        for line in p.stdout:
            fo.write(zc.compress(line))
        fo.write(zc.flush())

def import_db(dump_file, db_name):
    start_cluster()
    if db_name in list_db():
        raise RuntimeError("A database of the same name already exists")
    create_db(db_name)
    import zlib
    zd = zlib.decompressobj()
    c = read_config()
    p = subprocess.Popen([os.path.join(os.path.dirname(c['pg_ctl_path']), "psql"), "-h", "localhost", "-p", c['port'], "-d", db_name], stdin = subprocess.PIPE)
    with open(dump_file, "rb") as fi:
        for chunk in iter(lambda: fi.read(2048), ''):
            p.stdin.write(zd.decompress(chunk))
        p.stdin.write(zd.flush())
        p.stdin.close()
    p.wait()

def psql(args):
    start_cluster()
    c = read_config()
    a = [os.path.join(os.path.dirname(c['pg_ctl_path']), "psql"), "-h", "localhost", "-p", c['port']]
    a += args
    p = subprocess.Popen(a)
    p.wait()

def print_cluster_status():
    if check_cluster():
        print("DB      \tPresent")
        c = read_config()
        for k, v in c.items():
            print("{}\t{}".format(k.ljust(10,' '), v))
        print("params    \t{}".format(cluster_params()))
        # call status
        if is_started():
            print("Started")
        else:
            print("Stopped")
    else:
        print("DB       \tAbsent")        

def print_usage():
    print("PGLite management tool. Commands:\n")
    print("init [path_to_pg_ctl]\tInitialize the cluster")
    print("reset\t\t\tReset the cluster")
    print("status\t\t\tPrint the status of the cluster")
    print("start\t\t\tStart the cluster")
    print("stop\t\t\tStop the cluster")
    print("create db_name\t\tCreate a database")
    print("drop db_name\t\tDrop a database")
    print("list\t\t\tList databases")
    print("export db_name file\tExport a database to a dump file")
    print("import file db_name\tCreate a new database and import data from the dump file")
    print("psql\t\t\tLaunch a psql shell on the cluster")

        
def main():
    if len(sys.argv) < 2 or sys.argv[1] == '--help' or sys.argv[1] == 'help' or sys.argv[1] == '-h':
        print_usage()
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
        check_cluster() or die("Cluster not present")
        stop_cluster()
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
        print_usage()
        exit(1)

if __name__ == '__main__':
    main()
            
