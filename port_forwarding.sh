#!/bin/bash
dc_ip="192.168.0.98"
interface="wlan0"
#Daytona USA: UDP 20675 | UDP 12079
sudo iptables -t nat -A PREROUTING -p udp --dport 20675 -i "$interface" -j DNAT --to-destination "$dc_ip":20675
sudo iptables -t nat -A PREROUTING -p udp --dport 12079 -i "$interface" -j DNAT --to-destination "$dc_ip":12079

#Driving Strikers: UDP 30099
sudo iptables -t nat -A PREROUTING -p udp --dport 30099 -i "$interface" -j DNAT --to-destination "$dc_ip":30099 

#ChuChu Rocket!: UDP 9789
sudo iptables -t nat -A PREROUTING -p udp --dport 9789 -i "$interface" -j DNAT --to-destination "$dc_ip":9789

#Ooga Booga: UDP 6001
sudo iptables -t nat -A PREROUTING -p udp --dport 6001 -i "$interface" -j DNAT --to-destination "$dc_ip":6001

#Alien Front Online: UDP 7980
sudo iptables -t nat -A PREROUTING -p udp --dport 7980 -i "$interface" -j DNAT --to-destination "$dc_ip":7980

#Dee Dee Planet: UDP 9879
sudo iptables -t nat -A PREROUTING -p udp --dport 9879 -i "$interface" -j DNAT --to-destination "$dc_ip":9879

#Worms World Party: TCP 17219
sudo iptables -t nat -A PREROUTING -p tcp --dport 17219 -i "$interface" -j DNAT --to-destination "$dc_ip":17219

#The Next Tetris: Online Edition: TCP/UDP 3512
sudo iptables -t nat -A PREROUTING -p tcp --dport 3512 -i "$interface" -j DNAT --to-destination "$dc_ip":3512
sudo iptables -t nat -A PREROUTING -p udp --dport 3512 -i "$interface" -j DNAT --to-destination "$dc_ip":3512

#Starlancer and PBA: TCP/UPD 2300-2400 | UDP 6500 | TCP/UDP 47624 | UDP 13139
sudo iptables -t nat -A PREROUTING -p tcp --dport 2300:2400 -i "$interface" -j DNAT --to-destination "$dc_ip":2300-2400
sudo iptables -t nat -A PREROUTING -p udp --dport 2300:2400 -i "$interface" -j DNAT --to-destination "$dc_ip":2300-2400
sudo iptables -t nat -A PREROUTING -p udp --dport 6500 -i "$interface" -j DNAT --to-destination "$dc_ip":6500
sudo iptables -t nat -A PREROUTING -p tcp --dport 47624 -i "$interface" -j DNAT --to-destination "$dc_ip":47624
sudo iptables -t nat -A PREROUTING -p udp --dport 47624 -i "$interface" -j DNAT --to-destination "$dc_ip":47624
sudo iptables -t nat -A PREROUTING -p udp --dport 13139 -i "$interface" -j DNAT --to-destination "$dc_ip":13139

#World Series Baseball 2K2: UDP 37171 | UDP 13713
sudo iptables -t nat -A PREROUTING -p udp --dport 37171 -i "$interface" -j DNAT --to-destination "$dc_ip":37171
sudo iptables -t nat -A PREROUTING -p udp --dport 13713 -i "$interface" -j DNAT --to-destination "$dc_ip":13713

#Floigan Bros: TCP 37001
sudo iptables -t nat -A PREROUTING -p tcp --dport 37001 -i "$interface" -j DNAT --to-destination "$dc_ip":37001

#Internet Game Pack: UDP 5656 | TCP 5011 | TCP 10500-10503
#NBA/NFL/NCAA 2K Series: UDP 5502 | UDP 5503 | UDP 5656 | TCP 5011 | TCP 6666
sudo iptables -t nat -A PREROUTING -p tcp --dport 5011 -i "$interface" -j DNAT --to-destination "$dc_ip":5011
sudo iptables -t nat -A PREROUTING -p tcp --dport 6666 -i "$interface" -j DNAT --to-destination "$dc_ip":6666
sudo iptables -t nat -A PREROUTING -p tcp --dport 10500:10503 -i "$interface" -j DNAT --to-destination "$dc_ip":10500-10503
sudo iptables -t nat -A PREROUTING -p udp --dport 5503 -i "$interface" -j DNAT --to-destination "$dc_ip":5503
sudo iptables -t nat -A PREROUTING -p udp --dport 5656 -i "$interface" -j DNAT --to-destination "$dc_ip":5656
sudo iptables -t nat -A PREROUTING -p udp --dport 5502 -i "$interface" -j DNAT --to-destination "$dc_ip":5502

#Planet Ring: UDP 7648 | UDP 1285 | UDP 1028
sudo iptables -t nat -A PREROUTING -p udp --dport 7648 -i "$interface" -j DNAT --to-destination "$dc_ip":7648
sudo iptables -t nat -A PREROUTING -p udp --dport 1285 -i "$interface" -j DNAT --to-destination "$dc_ip":1285
sudo iptables -t nat -A PREROUTING -p udp --dport 1028 -i "$interface" -j DNAT --to-destination "$dc_ip":1028
