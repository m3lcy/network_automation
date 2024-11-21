import netmiko

ip = '172.16.12.225'
username = 'cisco'
password = 'cisco'
device_type = 'cisco_ios'
port = 22 

net_connect = netmiko.ConnectHandler(
    ip = ip,
    device_type = device_type,
    username = username,
    password = password, 
    port = port
 )
 
 show_ip_route = net_connect.send_command('show ip route') 
 print(show_ip_route)
