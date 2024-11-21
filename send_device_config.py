from netmiko import ConnectHandler


HOST = "172.16.12.225" 
USER = "cisco" 
PASS = "cisco"
TYPE = "cisco_ios"

dls1 = ConnectHandler(host=HOST, username=USER, password=PASS, device_type=TYPE)


# Inside the python environment
commands = [
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

dls1.send_config_set(commands)

dls1.send_command('write memory')

dls1.disconnect()
