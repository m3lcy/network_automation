from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_configure, napalm_get
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.files import write_file
from pathlib import Path
from datetime import datetime
import logging 
import os
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2 import Template

def replace_config(task: Task, template_file: str, timestamp: str = None, dry_run: bool = True):
    if timestamp is None or timestamp == "manual":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try: 
        BASE_DIR = Path(__file__).resolve().parents[2]   
        TEMPLATE_DIR = BASE_DIR / "templates"
        
        template_path = TEMPLATE_DIR / template_file
        data_path = BASE_DIR / "data" / f"{task.host.name}.yaml"

        if not template_path.exists():
            msg = f"Golden template not found: {template_path}"
            logging.error(msg)
            return Result(
                host = task.host,
                failed = True,
                result = msg
            )
        
        device_vars = {}
        if data_path.exists():
            with open(data_path, "r") as f:
                device_vars = yaml.safe_load(f) or {}

        env = Environment(
            loader = FileSystemLoader(str(TEMPLATE_DIR)),
            undefined = StrictUndefined,
            trim_blocks = True,
            lstrip_blocks = True
        )
        template = env.get_template(template_file)
        golden_config = template.render(**device_vars, host = task.host)

        rendered_dir = Path("golden_configs/rendered/") / task.host.name
        rendered_dir.mkdir(parents=True, exist_ok=True)
        rendered_filename = rendered_dir / f"{task.host.name}_{template_file}_{timestamp}.rendered.cfg"
        
        with open(rendered_filename, "w") as f:
            clean_lines = [line.rstrip() for line in golden_config.splitlines() if line.strip()]
            f.write("\n".join(clean_lines) + "\n")
        
        os.chmod(rendered_filename, 0o444)
        logging.info(f"Full golden rendered config saved for {task.host.name} ({task.host.hostname}): {rendered_filename}")

        backup_dir = f"outputs/backups"
        os.makedirs(backup_dir, exist_ok = True)
        backup_filename = f"{backup_dir}/{task.host.name}_{timestamp}_pre-replace.cfg"

        backup_result = task.run(
            task = napalm_get,
            getters = ["config"],
            retrieve = "running"
        )
        running = backup_result.result["config"]["running"]
        task.run(
            task = write_file,
            filename = backup_filename,
            content = running
        )
        os.chmod(backup_filename, 0o444)
        logging.info(f"First saving backup for {task.host.name} ({task.host.hostname}) before continuing..: {backup_filename}")



        if dry_run:
            result = task.run(
                task = napalm_configure,
                configuration = golden_config,
                replace = True,             # replace; keep True
                dry_run = True
            )
        else:
            try:
                result = task.run(
                    task = napalm_configure,
                    configuration = golden_config,
                    replace = True,
                    dry_run = False
                )
            except Exception as commit_error:
                logging.error(f"Commit failed on {task.host.name} ({task.host.hostname}): {commit_error} ROLLING BACK TO OLD CONFIG...")
                task.run(
                    task = napalm_configure,
                    configuration = running,
                    replace = True,
                    dry_run = False
                )
                logging.info(f"ROLLED BACK successfully on {task.host.name} ({task.host.hostname})")
                return Result(
                    host = task.host,
                    failed = True,
                    result = f"COMMIT FAILED; ROLLED BACK: {commit_error}"
                )

        diff_output = ""
        if dry_run and result[0].diff:
            diff_output = result[0].diff
        elif not dry_run:
            diff_output = "COMMITTED - no diff available after commit"

        diffs_dir = f"outputs/diffs"
        os.makedirs(diffs_dir, exist_ok = True)
        diff_filename = f"{diffs_dir}/{task.host.name}_napalm_replace_{timestamp}.diff"

        with open(diff_filename, "w") as df:
            df.write(diff_output or "No diff generated.\n")
        os.chmod(diff_filename, 0o444)

        # dry-run (default)
        if dry_run:
            logging.info(f"Dry-run replace DIFF for {task.host.name} ({task.host.hostname}): {diff_filename}")
            return Result(
                host = task.host,
                result = f"Dry-run replace DIFF completed for {task.host.name} ({task.host.hostname})"
            )
        
        # commit
        logging.info(f"Config replace COMMITTED for {task.host.hostname} ({task.host.hostname}): {diff_filename}")
        return Result(
            host = task.host,
            result = f"Config replace COMMITTED completed for {task.host.name} ({task.host.hostname})"
        )
    
    except Exception as e:
        logging.error(f"Replace failed for {task.host.name} ({task.host.hostname}): {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Replace failed {e}"
        )