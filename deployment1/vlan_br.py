from netmiko import ConnectHandler
import yaml
import os

with open('vlans.yml') as file:
    vlans = yaml.safe_load(file)['vlans']

with open('devices.yml') as file:
    devices = yaml.safe_load(file)['devices']

os.makedirs("logs", exist_ok=True)

try:
    for device in devices:
        net_connect = ConnectHandler(
            host = device['host'],
            username = device['username'],
            password = device['password'],
            device_type = device['device_type']
        )

        sh_vlan_br = net_connect.send_command('show vlan brief')
        log_file = f"logs/{device['host']}_vlan_logs.txt"

        with open(log_file, 'a') as file:
            for vlan in vlans:
                vlan_id = str(vlan['id'])
                vlan_name = vlan['name']

                if vlan_id in sh_vlan_br:
                    print(f"[SKIPPED] VLAN already exists in {device['host']}")
                else:
                    print(f"Creating VLAN on {device['host']}")
                    config_commands = [
                        f"vlan {vlan_id}",
                        f"name {vlan_name}"
                    ]
                    net_connect.send_config_set(config_commands)
                    file.write(f"[CREATED] VLAN {vlan_id} {vlan_name} created) on {device['host']}\n")

except Exception as e:
    print("Could not connect to {device['host']}: Error {e}")

finally:
    if 'net_connect' in locals():
        net_connect.disconnect()
        print(f"Disconnected from {device['host']}")
    else:
        print("No connection to disconnect")