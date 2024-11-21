from netmiko import ConnectHandler


HOST = "10.254.0.1" 
USER = "cisco" 
PASS = "cisco"
TYPE = "cisco_xe"

r1 = ConnectHandler(host=HOST, username=USER, password=PASS, device_type=TYPE)