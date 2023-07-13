import socket
import threading

global car_state
global car_info


class Car:
	name = None
	addr = None

	def __init__(self, name, addr):
		self.name = name
		self.addr = addr

	def __str__(self):
		return '{}-{}'.format(self.name, self.addr)


def server_receive(socket: socket.socket):
	global car_state
	global car_info
	while True:
		data = socket.recvfrom(1024)
		msg = data[0].decode()
		addr = data[1]
		msg_split = msg.split('-')
		code = msg_split[1]
		match msg_split[0]:
			case 'query':
				state = car_state.get(code)
				if state is None:
					socket.sendto('error-need_register'.encode(), (addr[0], 48976))
				else:
					socket.sendto('success-{}-{}'.format(state,car_info.get(code)).encode(), (addr[0], 48976))
			case 'register':
				car_state[code]='online'
				new_info = Car(msg_split[2], msg_split[3])
				car_info[code]= new_info
			case 'heartbeat':
				if car_state.get(code) != 'online':
					car_state[code]='online'
			case 'update':
				new_info = Car(msg_split[2], msg_split[3])
				car_info[code]=new_info
		print(msg)


if __name__ == "__main__":
	global car_state
	car_state = {}
	car_info = {}
	socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socket.bind(('', 48976))
	threading.Thread(target=server_receive(socket)).start()
