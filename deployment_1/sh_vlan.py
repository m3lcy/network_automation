from netmiko import ConnectHandler
import yaml
import json
import os

with open('vlans.yml') as (f):
    vlans = yaml.safe_load(f)['vlans']

with open('devices.yml') as (f):
    devices = yaml.safe_load(f)['devices']

os.makedirs("logs", exist_ok=True)

try:
    for device in devices:
        net_connect = ConnectHandler(
            host = device['host'],
            username = device['username'],
            password = device['password'],
            device_type=device['device_type']
        )

        sh_vlan = net_connect.send_command('show vlan')
        log_file = f"logs/{device['host']}_vlan_log.txt"

        with open(log_file, 'a') as f:
            for vlan in vlans:
                vlan_id = str(vlan['id'])
                vlan_name = (vlan['name'])

                if vlan_id in sh_vlan:
                    print(f"VLAN {vlan_id} EXISTS ON {device['host']}")
                else:
                    print(f"VLAN DOES NOT EXIST ON {device['host']}")
            
except Exception as e: 
    print(f"Failed to connect to {device['host']}: Error {e}")

finally:
    if net_connect:
        net_connect.disconnect()
        print(f"Disconnected from {device['host']}")
    else:
        print(f"No connection to disconnect from")