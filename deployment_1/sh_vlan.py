from netmiko import ConnectHandler
from datetime import datetime
import logging
import yaml
import json
import os

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs(f'outputs/vlan_reports/{timestamp}', exist_ok = True)
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename = f'logs/verify_vlans_{timestamp}.log',
    level = logging.INFO,
    format = '%(asctime)s = %(levelname)s = %(message)s'
)

with open('configs/devices.yml') as (f):
    devices = yaml.safe_load(f)['devices']

with open('configs/vlans.yml') as (f):
    vlans = yaml.safe_load(f)['vlans']

password = os.getenv('DEVICE_PASS')
if not password:
    raise EnvironmentError('DEVICE_PASS not set in environment.')


for device in devices:
    net_connect = None
    try:
        net_connect = ConnectHandler(
            host = device['host'],
            username = device['username'],
            password = password,
            device_type = device['device_type']
        )
        logging.info(f"Connected to {device['device_name']} ({device['host']})")

        sh_vlan = net_connect.send_command('show vlan')
        log_file = f"logs/{device['device_name']}_vlan_log.cfg"

        with open(log_file, 'a') as f:
            for vlan in vlans:
                vlan_id = str(vlan['id'])
                vlan_name = (vlan['name'])

                if vlan_id in sh_vlan:
                    print(f"VLAN {vlan_id} EXISTS ON {device['device_name']} ({device['host']})")
                else:
                    print(f"VLAN DOES NOT EXIST ON {device['device_name']} ({device['host']})")
            
    except Exception as e:
        logging.error(f"Error: {e}")
                      
    finally:
        if net_connect:
            net_connect.disconnect()
            logging.info(f"Disconnected from {device['device_name']} ({device['host']})")
        else:
            logging.warning(f"Could not connect to {device['device_name']} ({device['host']})")