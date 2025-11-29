from nornir_netmiko import netmiko_send_config, netmiko_send_command
from nornir.core.task import Result
import logging
import os

def send_config(task, timestamp):
    try:
        global_cmds = [
            'banner motd ^Authorized Access Only!!!^',
            'service password-encryption',
            'ip routing',
            'crypto key generate rsa usage-keys label ssh-key modulus 1024',
            'no ip domain-lookup',
            'ip domain-name cisco.com'
        ]

        task.run(
            task = netmiko_send_config,
            config_commands = global_cmds
        )
        logging.info(f"Sent {len(global_cmds)} global commands to {task.host.name} ({task.host.hostname})")
        
        specific_cmds = task.host.data.get("custom_commands", [])
        if specific_cmds:
            task.run(
                task = netmiko_send_command,
                config_commands = specific_cmds
            )

        show_run = task.run(
            task = netmiko_send_config,
            command_string = "show run"
        )

        filename = f"outputs/{task.host.name}_config_{timestamp}.cfg"
        with open(filename, "w") as f:
            f.write(show_run.result)
        os.chmod(filename, 0o444)

        return Result(
            host = task.host,
            result = f"Configuration applied to {task.host.name} ({task.host.hostname}) successfully!"
        )

    except Exception as e:
        logging.error(f"Error collecting info from {task.hostname.name} ({task.host.hostname}). Error: {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Error collecting info: {e}"
        )