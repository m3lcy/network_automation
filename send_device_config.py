from netmiko import ConnectHandler


HOST = "172.16.12.225" 
USER = "cisco" 
PASS = "cisco"
TYPE = "cisco_xe"

r1 = ConnectHandler(host=HOST, username=USER, password=PASS, device_type=TYPE)