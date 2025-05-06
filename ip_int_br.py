from netmiko import ConnectHandler


devices = [
    {
        'host' : '192.168.1.1',
        'username' : 'admin',
        'password' : 'cisco',
        'device_type' : 'cisco_ios',
        'port' : 22,
        'device_name' : 'core_r1'
    },
    {
        'host' : '192.168.1.2',
        'username' : 'admin',
        'password' : 'cisco',
        'device_type' : 'cisco_ios',
        'port' : 22,
        'device_name' : 'core_r2'
    }
]

for device in devices:
    net_connect = None
    try:
        net_connect = ConnectHandler(
            host=device['host'],
            username=device['username'],
            password=device['password'],
            device_type=device['device_type'],
            port=device['port']
        )

        show_running_config = net_connect.send_command('show running-config')
        print(f"Output for {device['device_name']}: {show_running_config}")

        filename = f"{device['device_name']}_running_config.txt"
        with open(filename,'w') as file:
            file.write(f"Output for {device['device_name']}: \n{show_running_config}\n")

    except Exception as e:
        print(f"Error {e}")

    finally:
        if net_connect:
            net_connect.disconnect()
            print(f"Disconnected from {device['device_name']}")
        else:
            print(f"No connection to disconnect")
