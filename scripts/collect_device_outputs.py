from netmiko import ConnectHandler
from datetime import datetime
import logging
import os


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

logging.basicConfig(
    filename = 'device_access.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )

password = os.getenv('DEVICE_PASS')

devices = [
    {
        'host' : '192.168.12.36',
        'username' : 'admin',
        'password' : password,
        'device_type' : 'cisco_ios',
        'device_name' : 'l3-sw-01',
        'port' : 22
    },
    {
        'host' : '192.168.12.37',
        'username' : 'admin',
        'password' : password,
        'device_type' : 'cisco_ios',
        'device_name' : 'l3-sw-02',
        'port' : 22
    },
    {
        'host' : '192.168.12.38',
        'username' : 'admin',
        'password' : password,
        'device_type' : 'cisco_ios',
        'device_name' : 'access-sw-01',
        'port' : 22
    },
    {
        'host' : '192.168.12.39',
        'username' : 'admin',
        'password' : password,
        'device_type' : 'cisco_ios',
        'device_name' : 'access-sw-02',
        'port' : 22
    },
    {
        'host' : '192.168.12.40',
        'username' : 'admin',
        'password' : password,
        'device_type' : 'cisco_ios',
        'device_name' : 'access-sw-03',
        'port' : 22
    },
    {
        'host' : '192.168.12.41',
        'username' : 'admin',
        'password' : password,
        'device_type' : 'cisco_ios',
        'device_name' : 'access-sw-04',
        'port' : 22
    }
]

for device in devices:
    net_connect = None
    try:
        net_connect = ConnectHandler(**device)
        logging.info(f"Connected to {device['device_name']}")

        commands = ['show ip interface brief',
                    'show ip route',
                    'show ip arp',
                    'show cdp neighbors',
                    'show ip ospf neighbor',
                    'show bgp summary'
                    ]
        outputs = {}
        for cmd in commands:
            outputs[cmd] = net_connect.send_command(cmd)
        logging.info(f"Collected {len(outputs)} command outputs from {device['device_name']}")

        filename = f"{device['device_name']}_outputs_{timestamp}.cfg"
        with open(filename,"x") as f:
            f.write(f"Output for {device['device_name']}: \n{outputs}\n")
        os.chmod(filename, 0o444)

    except Exception as e:
        logging.error(f"Error {e}")

    finally:
        if net_connect:
            net_connect.disconnect()
            logging.info(f"Disconnected from device {device['device_name']} {device['host']}")
        else:
            logging.warning(f"Could not connect to {device['device_name']} {device['host']}")