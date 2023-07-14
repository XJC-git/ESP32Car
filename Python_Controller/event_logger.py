import datetime


class EventLogger:
	def __init__(self,role):
		self.role = role
		if role=='controller':
			self.role_str='\033[33m[Controller]\033[0m'
		else:
			self.role_str='\033[31m[Controller]\033[0m'
	def key_press(self,key):
		self.log('\033[34mKey[{}]Press Down\033[0m'.format(key.char))
	def key_release(self,key):
		self.log('\033[34mKey[{}]Release\033[0m'.format(key.char))

	def log(self,str):
		dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		print('[{}]{}{}'.format(dt_ms,self.role_str,str))