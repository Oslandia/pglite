#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import os
import sys
if sys.version_info.major == 3:
    import configparser as ConfigParser
else:
    import ConfigParser
import subprocess

# global configuration file
PGLITE_CONF = 'pglite.conf'
# base directory
PGLITE_DB_DIR = os.path.join(os.path.expanduser("~"), ".pglite")
# configuration file
PGLITE_DB_CONF = os.path.join(PGLITE_DB_DIR, "db.conf")
# directory where Postgresql data are written
PGLITE_DB_PGDATA = os.path.join(PGLITE_DB_DIR, "pg_data")
# don't export tables in _tempus_import
PGLITE_EXTRA_DUMP_OPTIONS = ["-N", "_tempus_import"]
PGLITE_DEFAULT_PORT = "55432"

def die(msg):
    raise RuntimeError(msg)

def write_config(c_dict):
    c = ConfigParser.ConfigParser()
    c.add_section("cluster")
    for k, v in c_dict.items():
        c.set("cluster", k, v)
    c.add_section("environment")
    with open(PGLITE_DB_CONF, 'w') as configfile:
        c.write(configfile)

def read_config():
    c = ConfigParser.ConfigParser()
    c.read(PGLITE_DB_CONF)
    return dict(c.items("cluster"))

def read_environement():
    env = dict(os.environ)
    # look for a global config file for environment variables
    paths = ['/etc']
    if "OSGEO4W_ROOT" in os.environ:
        paths.append(os.path.join(os.environ["OSGEO4W_ROOT"], 'etc'))
    paths.append(os.path.abspath(os.path.dirname(__file__)))
    for p in paths:
        f = os.path.join(p, PGLITE_CONF)
        if os.path.isfile(f):
            c = ConfigParser.ConfigParser()
            c.read(f)
            for k, v in c.items("environment"):
                env[k] = v
    return env

def check_cluster():
    """Check if db exists"""
    return os.path.isdir(PGLITE_DB_DIR) and os.path.isfile(PGLITE_DB_CONF) and os.path.isdir(PGLITE_DB_PGDATA)

def find_pg_ctl():
    """Find the pg_ctl executable in common places"""
    if sys.platform.startswith('linux'):
        paths = ['/usr/lib/postgresql/11/bin/pg_ctl',
                 '/usr/lib/postgresql/10/bin/pg_ctl',
                 '/usr/lib/postgresql/9.6/bin/pg_ctl',
                 '/usr/lib/postgresql/9.5/bin/pg_ctl',
                 '/usr/lib/postgresql/9.4/bin/pg_ctl',
                 '/usr/lib/postgresql/9.3/bin/pg_ctl']
        paths += [os.path.join(path, 'pg_ctl') for path in os.environ['PATH'].split(':')]
    elif sys.platform.startswith('freebsd'):
        paths = [sys.exec_prefix+'/bin/pg_ctl']
    else: # Windows
        paths = [ os.path.join(os.environ["OSGEO4W_ROOT"], "bin", "pg_ctl.exe"),
                  os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "11", "bin", "pg_ctl.exe"),
                  os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "10", "bin", "pg_ctl.exe"),
                  os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "9.6", "bin", "pg_ctl.exe"),
                  os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "9.5", "bin", "pg_ctl.exe"),
                  os.path.join(os.environ["ProgramFiles"], "PostgreSQL", "9.4", "bin", "pg_ctl.exe")]
    for p in paths:
        if os.path.isfile(p):
            #print("Found pg_ctl at " + p)
            return p
    return None

def init_cluster(pg_ctl_path=None):
    """
    Initialize a db directory
    @param pg_ctl_path the path to the pg_ctl executable. If None, it will be looked for
    """
    if check_cluster():
        # nothing to do
        #print("Cluster already present")
        return
    if pg_ctl_path is None:
        pg_ctl_path = find_pg_ctl() or die("Can't find pg_ctl")
    subprocess.Popen([os.path.join(os.path.dirname(pg_ctl_path), "initdb"), "-D", PGLITE_DB_PGDATA, "-EUTF8"]).communicate()

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
    flags = 0
    if sys.platform == "win32":
        flags = 0x08000000 # CREATE_NO_WINDOW
        print("Starting PostgreSQL ...")
    subprocess.Popen([c['pg_ctl_path'], "start", "-w", "-D", PGLITE_DB_PGDATA, "-l", os.path.join(PGLITE_DB_DIR, "postgresql.log")],
        creationflags = flags,
        env=read_environement()).communicate()    

def stop_cluster(shutdown_mode="fast"):
    """
    shutdown_mode = smart, fast or immediate
    """
    if not is_started():
        # nothing to do
        #print("DB already stopped")
        return
    c = read_config()
    print("Shutting down in {} mode ...".format(shutdown_mode))
    subprocess.Popen([c['pg_ctl_path'], "stop", "-D", PGLITE_DB_PGDATA, "-m", shutdown_mode]).communicate()

def cluster_params():
    c = read_config()
    return "host=localhost port={}".format(c['port'])

def is_started():
    c = read_config()
    out, err = subprocess.Popen([c['pg_ctl_path'], "status", "-D", PGLITE_DB_PGDATA],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                universal_newlines=True).communicate()
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
    out, err = subprocess.Popen([os.path.join(os.path.dirname(c['pg_ctl_path']), "psql"), "-h", "localhost", "-p", c['port'], "-t", "-c", sql, "postgres"],
                                stdout = subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                universal_newlines=True).communicate()
    return [x.strip() for x in out.split('\n')[:-2]]

def export_db(db_name, dump_file):
    start_cluster()
    import zlib
    zc = zlib.compressobj()
    c = read_config()
    a = [os.path.join(os.path.dirname(c['pg_ctl_path']), "pg_dump"), "-h", "localhost", "-p", c['port'], "-d", db_name, "-O", "-x"]
    a += PGLITE_EXTRA_DUMP_OPTIONS
    p = subprocess.Popen(a, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
    p.stdin.close()
    with open(dump_file, "wb") as fo:
        for line in p.stdout:
            fo.write(zc.compress(line))
        fo.write(zc.flush())
    p.wait()

def import_db(dump_file, db_name):
    start_cluster()
    if db_name in list_db():
        raise RuntimeError("A database of the same name already exists")
    create_db(db_name)
    import zlib
    zd = zlib.decompressobj()
    c = read_config()
    p = subprocess.Popen([os.path.join(os.path.dirname(c['pg_ctl_path']), "psql"), "-h", "localhost", "-p", c['port'], "-d", db_name], stdin = subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    with open(dump_file, "rb") as fi:
        for chunk in iter(lambda: fi.read(2048), b''):
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

