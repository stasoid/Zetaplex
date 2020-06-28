import socket, thread

CONNECTING = 0
LISTENING = 1
CANT_CONNECT = 1
CONNECTED = 2
CONNECTION_CLOSED = 3
UNKNOWN = 4

class SockControll:
	__slots__ = ['close']

	def __init__(self):
		self.close = False

	def stop(self):
		self.close = True

def fork(callback, check, *args, **kwargs):
	controll = SockControll()
	def thread_trigger():
		try:
			result, error = check(*args, **kwargs), None
		except Exception, e:
			result, error = None, e
		if not controll.close:
			callback(result, error)
	thread.start_new_thread(thread_trigger, ())
	return controll

class SockListen:
	status = LISTENING

	def __init__(self, port, size, maxqueue, socklist):
		self.port = port
		self.size = size
		self.socklist = socklist
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.sock.bind(('', port))
		self.sock.listen(maxqueue)

	def close(self):
		self.status = CONNECTION_CLOSED
		self.sock.close()
		self.sock = None

	def accept(self):
		try:
			sock,addr = self.sock.accept()
			socklist.append(Socket(addr, self.port, self.size, sock))
			return len(socklist) - 1
		except:
			return -2

class Socket:
	status = CONNECTING
	buffer = ''

	def __init__(self, ip, port, size, sock=None):
		self.ip = ip
		self.port = port
		self.size = size
		if sock:
			self.status = CONNECTED
			self.sock = sock
			self.controll = SockControll()
		else:
			self.controll = fork(self.addr_lookup, socket.getaddrinfo, self.ip, self.port, 0, socket.SOCK_STREAM)

	def disconnect(self, status=UNKNOWN):
		self.status = status
		if self.sock:
			self.sock.close()
			self.sock = None
		if self.controll:
			self.controll.stop()
			self.controll = None

	def addr_lookup(self, result, error):
		if error:
			self.disconnect(CANT_CONNECT)
		else:
			for f, t, p, c, a in result:
				try:
					self.sock = socket.socket(f, t, p)
				except:
					continue
				self.controll = fork(self.connect, self.sock.connect, a)
				break
			else:
				self.disconnect(CANT_CONNECT)

	def connect(self, result, error):
		if error:
			self.disconnect(CANT_CONNECT)
		else:
			self.controll = SockControll()
			self.status = CONNECTED
			if not self.controll.close:
				self.controll = fork(self.bufferadd, self.sock.recv, self.size)

	def bufferadd(self, result, error):
		if error:
			self.disconnect(UNKNOWN)
		elif not result:
			self.disconnect(CONNECTION_CLOSED)
		else:
			self.buffer += result
			if not self.controll.close:
				self.controll = fork(self.bufferadd, self.sock.recv, self.size)

	def readbytes(self, bytes):
		if self.status == CONNECTED:
			read = self.buffer[:4]
			self.buffer = self.buffer[4:]
			if read:
				return [ord(b) for b in read]
			else:
				return 0
		else:
			return -1

	def readupto(self, end):
		if self.status == CONNECTED:
			print '      End: %s Buffer: %s' % (repr(end),repr(self.buffer))
			read = self.buffer.split(end)[0]
			self.buffer = self.buffer[len(read+end):]
			print '      Read: %s' % read
			if read:
				return [ord(c) for c in read] + [0]
			else:
				return 0
		else:
			return -1

	def send(self, text):
		if self.status == CONNECTED:
			self.sock.send(text)