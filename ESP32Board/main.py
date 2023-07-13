from machine import Pin,PWM
import time
import network,usocket

#Launch WIFI client and connect to controller
#Init Wifi LED
WIFI_LED=Pin(2, Pin.OUT, value=1)
wlan = network.WLAN(network.STA_IF) #STA Mode
wlan.active(True)
wlan.connect('X', '70xc1227')
while not wlan.isconnected():
     #LED flash
    WIFI_LED.value(0)
    time.sleep_ms(300)
    WIFI_LED.value(1)
    time.sleep_ms(300)
     

socket=usocket.socket(af=AF_INET,type=SOCK_DGRAM,proto=IPPROTO_UDP)
socket.bind('',48975)
while True:
    data=socket.recvfrom(1024)
    print(data.decode())
