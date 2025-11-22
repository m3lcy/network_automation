from nornir import InitNornir
from nornir_netmiko import netmiko_send_config
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Result
from datetime import datetime
import logging
import os
import yaml
import hvac

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("logs", exist_ok = True)
os.makedirs("outputs", exist_ok = True)

logging.basicConfig(
    filename = "logs/device_access.log",
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

vault_addr = os.getenv("VAULT_ADDR")
vault_token = os.getenv("VAULT_TOKEN")

if not vault_addr or not vault_token:
    raise EnvironmentError("Vault environment variables VAULT_ADDR or VAULT_TOKEN not set.")

vault_client = hvac.Client(url = vault_addr, token = vault_token)
if not vault_client.is_authenticated():
    raise ConnectionError("Unable to authenticate to Vault. Check token or vault address")

nr = InitNornir(config_file = "config.yaml")  

def get_device_credentials(host):
    secret_path = f"network/devices/{host.name}"
    try:
        response = vault_client.secrets.kv.read_secret_version(
            path = secret_path,
            raise_on_deleted_version = True
        )

        data = response["data"]["data"]

        host.username = data.get("username", host.username)
        host.password = data["login_password"]
        host.data["secret"] = data["enable_secret"]

        logging.info(f"Credentials retrieved for {host.name} ({host.hostname}) from Vault")

    except Exception as e:
        logging.error(f"Error retrieving secrets for {host.name} ({host.hostname}) from Vault: {e}")
        raise

for host_obj in nr.inventory.hosts.values():
    try:
        get_device_credentials(host_obj)
    except Exception as e:
        logging.error(f"Skipping {host_obj.name} ({host_obj.hostname}) due to Vault error: {e}")

def send_device_config(task):
    try:
        global_commands = [
            'banner motd ^Authorized Access Only!!!^',
            'service password-encryption',
            'ip routing',
            'crypto key generate rsa usage-keys label ssh-key modulus 1024',
            'no ip domain-lookup',
            'ip domain-name cisco.com'
        ]
        task.run(
            task = netmiko_send_config,
            config_commands = global_commands
        )
        logging.info(f"Sent {len(global_commands)} global config commands to {task.host.name} ({task.host.hostname})")
       
        specific_commands = task.host.data.get("custom_commands", [])
        if specific_commands:
            task.run(
                task = netmiko_send_config,
                config_commands = specific_commands
            )

        show_run = task.run(
            task = netmiko_send_command,
            command_string = "show run",
            use_testfsm = False
        )

        filename = f"outputs/{task.host.name}_config_{timestamp}.txt"
        with open(filename, "x") as f:
            f.write(show_run.result)
        os.chmod(filename, 0o444)

        return Result(
            host = task.host,
            result = f"Configuration applied to {task.host.name} ({task.host.hostname})"
        )

    except Exception as e:
        logging.error(f"Error collecting info from {task.host.name} ({task.host.hostname}): {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Error collecting info: {e}"
        )

results = nr.run(task = send_device_config)
print_result(results)
logging.info("Nornir run complete.")