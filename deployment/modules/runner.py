import argparse
from pathlib import Path
from nornir.core.filter import F

def get_common_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", help="Jinja2 template or snippet file")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Dry-run (default)")
    group.add_argument("--commit", action="store_true", help="Commit changes")
    parser.add_argument("--limit", type=str, help="Limit to host(s): name, contains, or regex")
    return parser

def run_task(nr, task_func, **task_kwargs):
    args = argparse.Namespace()
    args.dry_run = not task_kwargs.pop("commit", False)
    args.limit = task_kwargs.pop("limit", None)

    if args.limit:
        nr = nr.filter(F(name=args.limit) | F(name__contains=args.limit) | F(name__regex=args.limit))

    result = nr.run(task=task_func, dry_run=args.dry_run, **task_kwargs)
    from nornir_utils.plugins.functions import print_result
    print_result(result)
    return result