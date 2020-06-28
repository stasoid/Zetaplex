import socks

class Data:
	def __init__(self, d):
		self.d = d
		self.data = {3:[255,255,255]}
		self.stack = 0
		self.graphics = range(8)
		self.files = []
		self.file = None
		self.keys = []
		self.mouse = [0,0]
		self.commands = {}
		self.cmdreturn = [0]*3
		self.keyrecord = []
		self.socklisten = None
		self.sockets = []
		self.socket = None
		self.variables = {}

	def between(self, n, mi, ma, t):
		if mi != None:
			n = max(mi,n)
		if ma != None:
			n = min(ma,n)
		return t(n)

	def peek(self, n=1, mi=None, ma=None, t=None, s=None):
		if s == None:
			s = self.stack
		l = self.len(s)
		if not l:
			r = [0]*n
		else:
			r = self.data[s][-n:]
			if n > l:
				r = [0] * (n - l) + r
			r.reverse()
		if t == None:
			t = type(n)
		r = [self.between(x,mi,ma,t) for x in r]
		if n == 1:
			return r[0]
		return r

	def push(self, value, s=None):
		if s == None:
			s = self.stack
		if not isinstance(value,list):
			v = [value]
		else:
			v = list(value)
			v.reverse()
		if not self.data.has_key(s):
			self.set(v, s)
		else:
			self.data[s].extend(v)

	def pop(self, mi=None, ma=None, t=None, s=None):
		if s == None:
			s = self.stack
		if not self.len(s):
			n = 0
		else:
			n = self.data[s].pop()
		if t == None:
			t = type(n)
		return self.between(n,mi,ma,t)

	def replace(self, rep, rwith, s=None):
		if s == None:
			s = self.stack
		for n in self.data[s]:
			if n == rep:
				n = rwith

	def index(self, x, n=1, s=None):
		if s == None:
			s = self.stack
		try:
			p = 1
			d = self.peek(self.len() + 1)
			while True:
				p = d.index(x,p - 1) + 1
				if n == 1:
					return p
				n -= 1
		except:
			return 0

	def get(self, n, len=1, mi=None, ma=None, t=float, s=None):
		if s == None:
			s = self.stack
		l = self.len(s) - n + 1
		end = min(l,len)
		if 1 > n or l < 1:
			return [self.between(0,mi,ma,t)] * len
		ret = self.data[s][l-end:l]
		ret.reverse()
		if end < len:
			ret += [self.between(0,mi,ma,t)] * (len - end)
		return ret

	def remove(self, n, a=0, s=None):
		if s == None:
			s = self.stack
		if self.len(s):
			self.data[s].reverse()
			try:
				while a != 0:
					self.data[s].remove(n)
					a -= 1
			except:
				pass
			self.data[s].reverse()

	def set(self, d, s=None):
		if s == None:
			s = self.stack
		self.data[s] = d

	def len(self, s=None):
		if s == None:
			s = self.stack
		if not self.data.has_key(s):
			return 0
		return len(self.data[s])

	def string(self):
		r = ''
		n = self.pop(t=int)
		while 0 < n < 256:
			r += chr(n)
			if n == 92:
				r += '\\'
			n = self.pop(t=int)
		try:
			return r.decode('string_escape')
		except:
			return r

	def graph(self, n):
		#0: Coords 1, 1: Coords 2, 2: Coords 3
		if n < 3:
			r = [self.pop(mi=0,ma=self.d.res[x],t=int,s=self.graphics[n]) for x in [0,1]]
			self.push(list(r), self.graphics[n])
		#3: Color 1, 4: Color 2
		elif 2 < n < 5:
			r = self.peek(3,0,255,int,self.graphics[n])
		#5: Radius, 6: Line width
		elif 4 < n < 7:
			r = self.peek(1,mi=1,t=int,s=self.graphics[n])
		#7: Fill options(0=no fill, 1=fill Color 1, 2=fill Color 2, 4=text background Color 2)
		elif n == 7:
			r = self.peek(1,0,2,int,self.graphics[n])
		return r

	def key(self):
		try:
			return self.keyrecord.pop()
		except:
			return 0

	def keypump(self):
		self.keyrecord = []

	def read(self, bytes=1):
		if 0 <= self.file < len(self.files) and self.files[self.file].mode == 'r':
			t = self.files[self.file].read(bytes)
			if not t:
				return -1
			return [ord(t[-x]) for x in range(1,len(t)+1)]

	def write(self, text):
		if 0 <= self.file < len(self.files) and self.files[self.file].mode == 'w':
			self.files[self.file].write(text)

	def close(self):
		if 0 <= self.file < len(self.files):
			self.files[self.file].close()
			del self.files[self.file]
			if self.file >= len(self.files):
				self.file -= 1

	def sockopen(self, ip, port, size=8192):
		self.sockets.append(socks.Socket(ip, port, size))
		self.socket = len(self.sockets) - 1
		return self.socket

	def listen(self, port, size=8192, maxqueue=5):
		if not self.socklisten:
			try:
				self.socklisten = socks.SockListen(port, size, maxqueue)
				return 1
			except:
				return -1
		return 0

	def accept(self):
		if self.socklisten:
			return self.socklisten.accept()
		else:
			return -1

	def readbytes(self, bytes, sock=None):
		if not sock:
			sock = self.socket
		if 0 <= sock <= len(self.sockets):
			return self.sockets[sock].readbytes(bytes)
		return -1

	def readupto(self, end, sock=None):
		if not sock:
			sock = self.socket
		if 0 <= sock <= len(self.sockets):
			return self.sockets[sock].readupto(end)
		return -1

	def send(self, text, sock=None):
		if not sock:
			sock = self.socket
		if 0 <= sock <= len(self.sockets):
			self.sockets[sock].send(text)

	def sockclose(self, sock=None):
		if not sock:
			sock = self.socket
		if 0 <= sock < len(self.sockets):
			self.sockets[sock].disconnect()
			del self.sockets[sock]
			if self.sock == len(self.files):
				self.sock -= 1