from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_configure
from pathlib import Path
from datetime import datetime
import logging 
import os
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2 import Template

def merge_config(task: Task, snippet_file: str, timestamp: str = None, dry_run: bool = True):
    if timestamp is None or timestamp == "manual":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        BASE_DIR = Path(__file__).resolve().parents[2]   
        TEMPLATE_DIR = BASE_DIR / "templates"
        SNIPPET_DATA_DIR = BASE_DIR / "snippet_data"
        
        snippet_path = TEMPLATE_DIR / snippet_file

        snippet_name = Path(snippet_file).stem.replace("_config", "")   
        snippet_data_path = SNIPPET_DATA_DIR / snippet_name / f"{task.host.name}.yaml"

        if not snippet_path.exists():
            msg = f"Snippet not found: {snippet_path}"
            logging.error(msg)
            return Result(host=task.host, failed=True, result=msg)
        
        device_vars = {}
        if snippet_data_path.exists():
            with open(snippet_data_path, "r") as f:
                device_vars = yaml.safe_load(f) or {}
            logging.info(f"Loaded snippet data from {snippet_data_path}")
        else:
            logging.warning(f"No snippet data found for {task.host.name} at {snippet_data_path} — rendering with empty vars")
            device_vars = {}

        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            undefined = StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template(snippet_file)
        rendered_snippet = template.render(**device_vars)

        rendered_dir = Path("golden_configs/rendered") / task.host.name
        rendered_dir.mkdir(parents=True, exist_ok=True)
        rendered_filename = rendered_dir/f"{task.host.name}_{snippet_file}_{timestamp}.rendered.cfg"
        
        with open(rendered_filename, "w") as f:
            f.write(rendered_snippet.strip() + "\n")
        os.chmod(rendered_filename, 0o444)
        logging.info(f"Rendered config saved: {rendered_filename}")

        result = task.run(
            task = napalm_configure,
            configuration = rendered_snippet,
            replace = False,            # no replace; keep False
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
        logging.info(f"Config merge COMMITTED for {task.host.name} ({task.host.hostname}): {diff_filename}")
        return Result(
            host = task.host,
            result = f"Merge COMMITTED completed for {task.host.name} ({task.host.hostname})"
        )
    
    except Exception as e:
        logging.error(f"Merge failed for {task.host.name} ({task.host.hostname}): {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Merge failed: {e}"
        )