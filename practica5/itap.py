ip = '192.168.1.2/24'
gw = '192.168.1.1'
    
system(f'sudo tunctl -u ger')
system(f'sudo ifconfig tap0 {ip} up')
system(f'sudo route add -net 192.168.1.0 netmask 255.255.255.0 gw {gw} dev tap0')