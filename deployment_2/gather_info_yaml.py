from netmiko import ConnectHandler
from datetime import datetime
import logging
import os
import yaml
import hvac

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

os.makedirs('logs', exist_ok = True)
os.makedirs('outputs', exist_ok = True)

logging.basicConfig(
    filename = 'logs/device_access.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )

vault_addr = os.getenv('VAULT_ADDR')
vault_token = os.getenv('VAULT_TOKEN')

if not vault_addr or not vault_token:
    raise EnvironmentError("Vault environment variables VAULT_ADDR or VAULT_TOKEN not set.")

vault_client = hvac.Client(url = vault_addr, token = vault_token)
if not vault_client.is_authenticated():
    raise ConnectionError("Unable to authenticate to Vault. Check token or vault address")

with open('configs/devices.yaml', 'r') as f:
    devices = yaml.safe_load(f)['devices']

def get_device_credentials(device_name):
    secret_path = f"network/devices/{device_name}"
    try:
        response = vault_client.secrets.kv.read_secret_version(
            path = secret_path,
            raise_on_deleted_version = True
            )
        data = response['data']['data']
        return data['login_password'], data['enable_secret']
    except Exception as e:
        logging.error(f"Error retrieving secrets for {device_name} from Vault: {e}")
        return None, None

for device in devices:
    net_connect = None
    name = device.get('device_name')
    host = device.get('host')
    username = device.get('username')

    try:
        password, secret = get_device_credentials(name)
        if not password or not secret:
            logging.error(f"No credentials found for {name}. Skipping...")
            continue

        netmiko_params = {
            'host': host,
            'username': username,
            'password': password,
            'secret': secret,
            'device_type': device.get('device_type', 'cisco_ios'),
            'port': device.get('port', 22)
        }

        net_connect = ConnectHandler(**netmiko_params)
        logging.info(f"Connected to {name} ({host})")
        net_connect.enable()

        commands = [
                'show ip interface brief',
                'show ip route',
                'show ip arp',
                'show cdp neighbors',
                'show ip ospf neighbor',
                'show bgp summary'
        ]
        outputs = {}
        for cmd in commands:
            outputs[cmd] = net_connect.send_command(cmd)
        logging.info(f"Collected {len(outputs)} command outputs from {name} ({host})")

        filename = f"outputs/{device['device_name']}_outputs_{timestamp}.cfg"
        with open(filename, "x") as f:
            yaml.safe_dump(outputs, f, default_flow_style = False)
        os.chmod(filename, 0o444)

    except Exception as e:
        logging.error(f"Error: {e}")

    finally:
        if net_connect:
            net_connect.disconnect()
            logging.info(f"Disconnected from device {name} ({host})")
        else:
            logging.warning(f"Could not connect to {name} ({host})")