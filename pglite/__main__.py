from .pglite import check_cluster, init_cluster, reset_cluster, start_cluster, stop_cluster, cluster_params, is_started, create_db, drop_db, list_db, export_db, import_db
import sys

def prt_params():
    print(cluster_params)

def prt_is_started():
    print("yes" if is_started() else "no")

def prt_list_db():
    print("\n".join(list_db())

no_arg_actions = {
        "check": check_cluster,
        "reset": reset_cluster,
        "start": start_cluster,
        "stop": stop_cluster,
        "params": prt_params,
        "is_started": prt_is_started,
        "list_db": prt_list_db,
        "init": init_cluster,
        }

one_arg_actions = {
    "init": init_cluster,
    "create_db": create_db,
    "drop_db": drop_db,
    "export_db": export_db,
    "import_db": import_db,
    }

usage = """
    usage python -m pglite <action> [arguments]

    actions are one of: 
    """+"\n\n        ".join(no_arg_actions.keys() + one_arg_actions.keys())

if len(sys.argv) < 2 or sys.argv[1] == "-h":
    print(usage)

action = sys.argv[1]

if action in no_arg_actions and len(sys.argv)==2:
    no_arg_actions[action]()
elif action in one_arg_actions and len(sys.argv)==3:
    one_arg_actions[action](sys.argv[2]
    

