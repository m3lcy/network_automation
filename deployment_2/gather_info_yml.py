from netmiko import ConnectHandler
from datetime import datetime
import logging
import os
import yaml

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

logging.basicConfig(
    filename = 'device_access.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )

password = os.getenv('DEVICE_PASS')
if not password:
    raise EnvironmentError('DEVICE_PASS not set in environment.')

with open('devices.yml', 'r') as f:
    devices = yaml.safe_load(f)['devices']

for device in devices:
    net_connect = None
    try:
        net_connect = ConnectHandler(
            host = device['host'],
            username = device['username'],
            password = password,
            device_type = device['device_type'],
            port = device['port']
        )
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

        filename = f"{device['device_name']}_outputs_{timestamp}.cfg"
        with open(filename,"x") as f:
            f.write(f"Output for {device['device_name']}: \n{outputs}\n")
        os.chmod(filename, 0o444)

    except Exception as e:
        logging.error(f"Error: {e}")

    finally:
        if net_connect:
            net_connect.disconnect()
            logging.info(f"Disconnected from device {device['device_name']} ({device['host']})")
        else:
            logging.warning(f"Could not connect to {device['device_name']} ({device['host']})")