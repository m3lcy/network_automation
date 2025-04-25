from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


host = "192.168.12.36" 
username = "admin" 
password = "cisco"
device_type = "cisco_ios"
port = 22
device_name = "dls1"

commands_vlan10 = [
    'interface vlan10',
    'ip address 172.16.12.1 255.255.255.224',
    'ip helper-address 172.16.12.226',
    'ip nat inside',
    'standby version 2',
    'standby 1 ip 172.16.12.254',
    'standby 1 priority 150',
    'standby 1 preempt',
    'no shutdown'
]

commands_vlan20 = [
    'interface vlan20',
    'ip address 172.16.12.33 255.255.255.224',
    'ip helper-address 172.16.12.226',
    'ip nat inside',
    'standby version 2',
    'standby 1 ip 172.16.12.254',
    'standby 1 priority 150',
    'standby 1 preempt',
    'no shutdown'
]

dls1 = None

try:
    dls1 = ConnectHandler(
    host = host,
    username = username,
    password = password,
    device_type = device_type,
    port = port
    )
    print(f"Connected to {device_name}")

    output_vlan10 = dls1.send_config_set(commands_vlan10)
    print(f"VLAN 10 configuration sent.")
    print(output_vlan10)

    output_vlan20 = dls1.send_config_set(commands_vlan20)
    print(f"VLAN 20 configuration sent.")
    print(output_vlan20)

    save_output = dls1.send_command('write memory')
    print(f"Save Output:")
    print(save_output)
    
except NetmikoAuthenticationException:
    print(f"Authentication failed for {device_name} ({host})")
except NetmikoTimeoutException:
    print(f"Connection to {device_name} ({host}) timed out")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if dls1: 
        dls1.disconnect()
        print(f"Disconnected from {device_name}")

