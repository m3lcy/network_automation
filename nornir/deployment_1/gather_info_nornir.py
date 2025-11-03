from nornir import InitNornir
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

        logging.info(f"Credentials retrieved for {host.name} from Vault")

    except Exception as e:
        logging.error(f"Error retrieving secrets for {host.name} from Vault: {e}")
        raise

for host_obj in nr.inventory.hosts.values():
    try:
        get_device_credentials(host_obj)
    except Exception as e:
        logging.error(f"Skipping {host_obj.name} due to Vault error: {e}")

def collect_device_info(task):
    try:
        commands = [
            "show ip interface brief",
            "show ip route",
            "show ip arp",
            "show cdp neighbors",
            "show ip ospf neighbor",
            "show bgp summary"
        ]
        outputs = {}
        for cmd in commands:
            result = task.run(task = netmiko_send_command, command_string = cmd)
            outputs[cmd] = result.result
            logging.info(f"Collecting data from {task.host.name} ({task.host.hostname})")
       
        filename = f"outputs/{task.host.name}_outputs_{timestamp}.yaml"
        with open(filename, "w") as f:
            yaml.safe_dump(outputs, f, default_flow_style=False)
        os.chmod(filename, 0o444)

        logging.info(f"Collected and saved {len(outputs)} command outputs from {task.host.name}")

        return Result(
            host = task.host,
            result = f"Collected {len(outputs)} commands from {task.host.name}"
        )

    except Exception as e:
        logging.error(f"Error collecting info from {task.host.name}: {e}")
        return Result(
            host = task.host,
            failed = True,
            result = f"Error collecting info: {e}"
        )

results = nr.run(task = collect_device_info)
print_result(results)
logging.info("Nornir run complete.")
