import threading
import time
import socket
import pynput

from Python_Controller.event_logger import EventLogger

key_state = {}
logger = EventLogger('controller')

ip = '192.168.31.36'
port = 48975


def heartbeat_handler(socket):
	global key_state
	while True:
		socket.sendto('heartbeat'.encode(), (ip, port))
		time.sleep(1)


if __name__ == "__main__":
	socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	threading.Thread(target=heartbeat_handler, args=(socket,)).start()
	while True:
		with pynput.keyboard.Events() as event:
			for i in event:
				key_event = i
				if isinstance(key_event, pynput.keyboard.Events.Press):  # 按下按键
					if not hasattr(key_event.key,'char'):
						match key_event.key:
							case pynput.keyboard.Key.right:
								socket.sendto('adjust-r'.encode(), (ip, port))
							case pynput.keyboard.Key.left:
								socket.sendto('adjust-l'.encode(), (ip, port))
							case pynput.keyboard.Key.space:
								if key_state.get(pynput.keyboard.Key.space) is None:
									key_state[pynput.keyboard.Key.space]=1
									socket.sendto('brake'.encode(), (ip, port))
						continue
					if key_state.get(key_event.key.char) is not None:
						continue
					else:
						key_state[key_event.key.char] = 1
						logger.key_press(key_event.key)
						match key_event.key.char:
							case 'w':
								socket.sendto('{}-0.6'.format(key_event.key.char).encode(), (ip, port))
							case 's':
								socket.sendto('{}-0.3'.format(key_event.key.char).encode(), (ip, port))
							case 'a':
								socket.sendto('{}-0.085'.format(key_event.key.char).encode(), (ip, port))
							case 'd':
								socket.sendto('{}-0.065'.format(key_event.key.char).encode(), (ip, port))
				elif isinstance(key_event, pynput.keyboard.Events.Release):  # 松开按键
					if not hasattr(key_event.key, 'char'):
						match key_event.key:
							case pynput.keyboard.Key.space:
								socket.sendto('brake-release'.encode(), (ip, port))
								del key_state[pynput.keyboard.Key.space]
						continue
					if key_state.get(key_event.key.char) is not None:
						del key_state[key_event.key.char]
						logger.key_release(key_event.key)
						socket.sendto('{}-stop'.format(key_event.key.char).encode(), (ip, port))
					else:
						pass
				break


