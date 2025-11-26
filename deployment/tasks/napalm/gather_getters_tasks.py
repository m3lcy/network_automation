from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.task import Result
import logging
import os
import yaml

def gather_getters(task, timestamp):
    try:
        getters = [
            'interfaces_ip',
            'arp_table',
            'lldp_neighbors',
            'bgp_neighbors',
            'vlans'
        ]

        result = task.run(
            task = napalm_get,
            getters = getters
        )

        data = result[0].result

        filename = f"outputs/{task.host.name}_napalm_getters_{timestamp}.yaml"
        with open(filename, "w") as f:
            yaml.safe_dump(data, f, default_flow_style = False)
        os.chmod(filename, 0o444)
        logging.info(f"Napalm data saved for {task.host.name} ({task.host.hostname}): {filename}")

        return Result(
            host = task.host,
            result = f"Napalm data collected for {task.host.name}"
        )

    except Exception as e:
        logging.error(f"Error collecting Napalm info from {task.host.name} ({task.host.hostname}): {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Error collecting Napalm info: {e}"
        )
