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
                task = netmiko_send_config,
                config_commands = specific_cmds
            )
            logging.info(f"Sent {len(specific_cmds)} custom commands to {task.host.name} ({task.host.hostname})")

        show_run = task.run(
            task = netmiko_send_command,
            command_string = "show run",
            use_textfsm=False
        )

        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok = True)
        filename = os.path.join(output_dir, f"{task.host.name}_config_{timestamp}.cfg")
        with open(filename, "w") as f:
            f.write(show_run.result)
        os.chmod(filename, 0o444)
        logging.info(f"Configuration saved for {task.host.name} ({task.host.hostname}): {filename}")

        return Result(
            host = task.host,
            result = f"Configuration applied to {task.host.name} ({task.host.hostname}) successfully!"
        )

    except Exception as e:
        logging.error(f"Error collecting info from {task.host.name} ({task.host.hostname}). Error: {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Error collecting info: {e}"
        )