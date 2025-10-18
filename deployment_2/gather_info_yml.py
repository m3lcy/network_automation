from netmiko import ConnectHandler
from datetime import datetime
import logging
import os
import yaml

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

os.makedirs('logs', exist_ok = True)
os.makedirs('outputs', exist_ok = True)

logging.basicConfig(
    filename = 'logs/device_access.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )

password = os.getenv('DEVICE_PASS')
if not password:
    raise EnvironmentError('DEVICE_PASS not set in environment.')

with open('configs/devices.yml', 'r') as f:
    devices = yaml.safe_load(f)['devices']

for device in devices:
    net_connect = None
    try:
        netmiko_params = {k: v for k, v in device.items() if k in ['host', 'username', 'device_type', 'port']}
        net_connect = ConnectHandler(**netmiko_params)
        logging.info(f"Connected to {device['device_name']} ({device['host']})")

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
        logging.info(f"Collected {len(outputs)} command outputs from {device['device_name']} ({device['host']})")

        filename = f"outputs/{device['device_name']}_outputs_{timestamp}.cfg"
        with open(filename,"x") as f:
            yaml.safe_dump(outputs, f, default_flow_style = False)
        os.chmod(filename, 0o444)

    except Exception as e:
        logging.error(f"Error: {e}")

    finally:
        if net_connect:
            net_connect.disconnect()
            logging.info(f"Disconnected from device {device['device_name']} ({device['host']})")
        else:
            logging.warning(f"Could not connect to {device['device_name']} ({device['host']})")