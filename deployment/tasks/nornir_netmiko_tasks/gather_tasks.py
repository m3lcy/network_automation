from nornir_netmiko import netmiko_send_command
from nornir.core.task import Result
import logging
import os
import yaml

def gather_info(task, timestamp):
    cmds = [
        'show ip interface brief',
        'show ip route',
        'show ip arp',
        'show cdp neighbors',
        'show ip ospf neighbor',
        'show bgp summary'
    ]
    outputs = {}

    for cmd in cmds:
        try:
            result = task.run(
                task = netmiko_send_command,
                command_string = cmd,
                use_textfsm = True
            )
            outputs[cmd] = result.result
            logging.info(f"Collected structured output from {task.host.name} ({task.host.hostname})")
        
        except Exception as e:
            logging.error(f"Error running command '{cmd}' for {task.host.name} ({task.host.hostname}): {e}")
            return Result(
                host = task.host,
                failed = True,
                result = f"Failed to run '{cmd}':{e}"
            )

    filename = os.path.join("outputs",f"{task.host.name}_info_{timestamp}.yaml")
    try:
        os.makedirs(os.path.dirname(filename), exist_ok = True)
        with open(filename, "w") as f:
            yaml.safe_dump(outputs, f, default_flow_style = False)
        os.chmod(filename, 0o444)
        logging.info(f"Gather info output saved for {task.host.name} ({task.host.hostname}): {filename}")

    except Exception as e:
        logging.error(f"Error collecting info from {task.host.name} ({task.host.hostname}). Error: {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Error collecting info: {e}"
        )

    return Result(
        host = task.host,
        result = f"Gather info data collected from {len(cmds)} commands on {task.host.name} ({task.host.hostname})" 
    )
    
