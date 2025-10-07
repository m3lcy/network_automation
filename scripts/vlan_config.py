from netmiko import ConnectHandler
import os

vlan_id = input("Enter the VLAN ID you want to create: ")
vlan_name = input("Enter the VLAN name you want to create: ")

devices = [
    {
        'host': '192.168.1.1',
        'username': 'core_r1',
        'password': 'cisco',
        'device_type': 'cisco_xr',
        'port': 22
    },
    {
        'host': '192.168.1.2',
        'username': 'core_r2',
        'password': 'cisco',
        'device_type': 'cisco_xr',
        'port': 22
    },
]

for device in  devices:
    try: 
        net_connect = ConnectHandler(
            host = device['host'],
            username = device['username'],
            password = device['password'],
            device_type = device['device_type'],
            port = device['port']
        )

        sh_vlan_br = net_connect.send_command('show vlan brief')

        if vlan_id in sh_vlan_br:
            print(f"VLAN {vlan_id} already exists on {device['host']}, Skipping...")
        else:
            print(f"Creating {vlan_id}...")
            net_connect.send_command([f"vlan {vlan_id}", f"name {vlan_name}"])

        os.makedirs('logs', exist_ok=True)

        with open(f"logs/{device['host']}_vlan.txt", 'w') as file:
            if vlan_id in sh_vlan_br:
                file.write(f"[SKIPPED] VLAN {vlan_id} already exists on {device['host']}\n")
            else:
                file.write(f"Creating VLAN {vlan_id} on {device['host']}\n")

    except Exception as e:
        print(f"Failed to connect to {device['host']}: Error {e}")

    finally:
        if 'net_connect' in locals():
            net_connect.disconnect()
            print(f"Successfully disconnected from {device['host']}")
        else:
            print(f"No connection to disconnect")
