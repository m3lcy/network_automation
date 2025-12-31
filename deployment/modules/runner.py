import argparse
from pathlib import Path
from nornir.core.filter import F

def get_common_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", nargs = "?", default = None, help="Jinja2 template or snippet file")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Dry-run (default)")
    group.add_argument("--commit", action="store_true", help="Commit changes")
    parser.add_argument("--limit", type=str, help="Limit to host(s): name, contains, or regex")
    return parser

def run_task(nr, task_func, **task_kwargs):
    commit = task_kwargs.pop("commit", False)
    limit = task_kwargs.pop("limit", None)

    dry_run = not commit

    if limit:
        if len(nr.filter(F(name=limit)).inventory.hosts) > 0:
            nr = nr.filter(F(name=limit))
        elif limit.startswith("group:"):
            group_name = limit[len("group:"):].strip()
            nr = nr.filter(F(groups__contains=group_name))
        else:
            nr = nr.filter(F(name__contains=limit) | F(name__regex=limit))


    if task_kwargs.pop("pass_dry_run", False):
        result = nr.run(task_func, dry_run = dry_run, **task_kwargs)
    else:
        result = nr.run(task = task_func, **task_kwargs)

    from nornir_utils.plugins.functions import print_result
    print_result(result)
    return result