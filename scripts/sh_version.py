from netmiko import ConnectHandler
import re

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
            host = devices['host'],
            username = devices['username'],
            password = devices['password'],
            device_type = devices['device_type']
        )

        sh_version = net_connect.send_command('show version')

        with open(f"device['host']_uptime_report.txt", 'w') as file:
            file.write(f"Output for device['host']: {sh_version}")

        pattern = 'sh_version'
        hostname = 'Device hostname is core_r1'
        
        result = re.search(pattern, hostname)
        print(result)

    except Exception as e:
        print(f"Error {e}")

    finally:
        if net_connect.disconnect():
            print(f"Successfully disconnected from {'host'}")
        else:
            print(f"No connection to disconnect")
