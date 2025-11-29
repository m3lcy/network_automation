from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_configure
from pathlib import Path
import logging 
import os
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2 import Template

def merge_config(task: Task, snippet_file: str, timestamp: str, dry_run: bool = True):
    try:
        snippet_path = Path("config_snippets") / snippet_file
        data_path = Path("data") / f"{task.host.name}.yaml"

        if not os.path.isfile(snippet_path):
            msg = f"Snippet not found: {snippet_path}"
            logging.error(msg)
            return Result(
                host = task.host,
                failed = True,
                result = msg
            )
        
        device_vars = {}
        if os.path.isfile(data_path):
            with open(data_path, "r") as f:
                device_vars = yaml.safe_load(f) or {}

        env = Environment(
            loader = FileSystemLoader("config_snippets"),
            undefined = StrictUndefined
        )
        template = env.get_template(snippet_file)
        rendered_snippet = template.render(**device_vars)

        result = task.run(
            task = napalm_configure,
            configuration = rendered_snippet,
            replace = False,
            dry_run = dry_run
        )

        diff_output = getattr(result[0], "diff", None) or result.result[0] or "No diff produced."
      
        diff_filename = f"outputs/{task.host.name}_napalm_merge_{timestamp}.cfg"
        with open(diff_filename, "w") as df:
            df.write(diff_output)
        os.chmod(diff_filename, 0o444)

        # dry-run (default)
        if dry_run:
            logging.info(f"Dry-run merge diff saved for {task.host.name} ({task.host.hostname}): {diff_filename}")
            return Result(
                host = task.host,
                result = f"Dry-run merge completed for {task.host.name} ({task.host.hostname})"
            )
        
        # commit
        logging.info(f"Config merge committed for {task.host.name} ({task.host.hostname}): {diff_filename}")
        return Result(
            host = task.host,
            result = f"Merge committed for {task.host.name} ({task.host.hostname})"
        )
    
    except Exception as e:
        logging.error(f"Merge failed for {task.host.name} ({task.host.hostname}): {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Merge failed: {e}"
        )