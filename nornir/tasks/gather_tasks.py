from nornir_netmiko import netmiko_send_command
from nornir.core.task import Result
import logging
import os
import yaml

def gather_info(task, timestamp):
    try:
        cmds = [
            'show ip interface brief',
            'show ip route',
            'show ip arp',
            'show cdp neighbors',
            'show ip ospf neighbor',
            'show bgp summary'
        ]
        outputs = {}

        for c in cmds:
            result = task.run(
                task = netmiko_send_command,
                command_string = c,
                use_textfsm = True
            )
            outputs[c] = result.result
            logging.info(f"Collected structured output from {task.host.name} ({task.host.hostname})")

            filename = f"outputs/{task.host.name}_structured_{timestamp}.yaml"
            with open(filename, "x") as f:
                yaml.safe_dump(outputs, f, default_flow_style = False)
            os.chmod(filename, 0o444)
            logging.info(f" Structured output saved for {task.host.name} ({task.host.hostname})")

            return Result(
                host = task.host,
                result = f"Structured data collected from {len(c)} commands from {task.host.name} ({task.host.hostname})" 
            )
        
    except Exception as e:
        logging.error(f"Error collecting info from {task.host.name} ({task.host.hostname}). Error: {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Error collecting info: {e}"
        )