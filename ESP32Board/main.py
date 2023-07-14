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
     

socket=usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM)
socket.bind(('',48975))

motor_forward=PWM(Pin(4),200,0)
motor_backward=PWM(Pin(27),200,0)
brake_led=Pin(22, Pin.OUT, value=0)
serve=PWM(Pin(21),50,0)
middle_angle=0.075
braking=False
while True:
    data=socket.recvfrom(1024)
    print(data)
    msg=data[0].decode()
    msg_split=msg.split('-')
    if msg_split[0]=='brake':
        if len(msg_split)==1:
            motor_forward.duty(1023)
            motor_backward.duty(1023)
            brake_led.value(1)
            braking=True
        else:
            motor_forward.duty(0)
            motor_backward.duty(0)
            brake_led.value(0)
            braking=False
    
    if braking and (msg_split[0]=='w'||msg_split[0]=='s'):
        continue
    if msg_split[0]=='w':
        if msg_split[1]=='stop':
            motor_forward.duty(0)
        else:
            motor_forward.duty(int(1023*float(msg_split[1])))
    elif msg_split[0]=='s':
        if msg_split[1]=='stop':
            motor_backward.duty(0)
        else:
            motor_backward.duty(int(1023*float(msg_split[1])))
    elif msg_split[0]=='a' or msg_split[0]=='d':
        if msg_split[1]=='stop':
            serve.duty(int(1023*middle_angle))
        else:
            serve.duty(int(1023*float(msg_split[1])))
    elif msg_split[0]=='adjust':
        if msg_split[1]=='r':
            middle_angle=middle_angle-0.001
        else:
            middle_angle=middle_angle+0.001
    
