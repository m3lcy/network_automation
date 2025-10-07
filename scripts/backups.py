from netmiko import ConnectHandler
import os
from time import time

devices = [
    {
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'cisco',
        'device_type': 'cisco_ios'
    },
    {
        'host': '192.168.1.2',
        'username': 'admin',
        'password': 'cisco',
        'device_type': 'cisco_ios'
    }
]

for device in devices:
    try: 
        net_connect = ConnectHandler(
            host = device['host'],
            username = device['username'],
            password = device['password'],
            device_type = device['device_type']
        )

        running_config = net_connect.send_command('show running-config')
        print(f"Output for {device['host']}: [running_config]")


        os.makedirs('backups', exist_ok=True)

        with open(f"backups/{device['host']}_running_config.txt", 'w') as file: 
            file.write(f"Output for {device['host']}")
            file.write(running_config)

    except Exception as e:
        print(f" Connection to {device['host']} failed: {e}")

    finally:
        if 'net_connect' in locals():
            net_connect.disconnect()
            print(f"Successfully disconnected from {device['host']}")
        else:
            print(f"No connection to disconnect")



