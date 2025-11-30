from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.task import Result
import logging
import os
import yaml

def backup_config(task, timestamp):
    try:
        result = task.run(
            task = napalm_get,
            getters = ["config"]
        )

        config = result[0].result["config"]["running"]

        os.makedirs("outputs/backups", exist_ok = True)

        filename = f"outputs/backups/{task.host.name}_napalm_backup_{timestamp}.cfg"
        with open(filename, "w") as f:
            f.write(config)
        os.chmod(filename, 0o444)
        logging.info(f"Backup saved for {task.host.name} ({task.host.hostname}): {filename}")

        return Result(
            host = task.host,
            result = f"Backup completed for {task.host.name} ({task.host.hostname})"
        )

    except Exception as e:
        logging.error(f"Backups failed for {task.host.name} ({task.host.hostname}): {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Backup failed: {e}"
        )