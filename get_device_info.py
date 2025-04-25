from netmiko import ConnectHandler

host = '192.168.12.36'
username = 'admin'
password = 'cisco'
device_type = 'cisco_ios'
port = 22
device_name = 'DLS1'

net_connect = None

try:
    net_connect = ConnectHandler(
        host = host,
        username = username,
        password = password,
        device_type = device_type,
        port = port,
    )

    show_ip_route = net_connect.send_command('show ip route')
    print(f"Output for {device_name}: {show_ip_route}")

    with open(f'{device_name}_ip_route.txt', 'w') as file:
        file.write(f"Output for {device_name}: \n{show_ip_route}\n")

except Exception as e:
    print(f"Error {e}")

finally: 
    if net_connect:
        net_connect.disconnect()
        print(f"Disconnected from {device_name}")
    else:
        print(f"No connection to disconnect.")



