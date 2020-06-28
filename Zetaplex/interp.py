import data
import pygame, random, sys, os, re, math
from string import digits
from pygame.locals import *

BASE = os.path.dirname(__file__)
DEBUG = False

def fullfile(file):
	return os.path.join(BASE, file)

class Debug:
	def __init__(self, on=True):
		self.on = on
		self.first = True
		if on:
			self.open()

	def p(self, text, end='\n', on=False):
		if self.on or on:
			try:
				self.file.write(text + end)
			except:
				self.toggle(False)

	def toggle(self, on=None):
		if on == None:
			on = not self.on
		if on:
			self.open()
		else:
			self.close()
		self.on = on

	def open(self):
		if self.first:
			mode = 'w'
			self.first = False
		else:
			mode = 'a'
		self.file = open('debug.txt', mode)

	def close(self):
		if self.on:
			self.file.close()
			self.on = False

debug = Debug(DEBUG)

class Interpreter:
	def __init__(self, d, s):
		d.clear()
		d.refresh()
		self.d = d
		self.source = s
		self.size = [max([len(l) for l in self.source]),len(self.source)]
		self.pos = [0,0]
		self.dir = 0
		self.data = data.Data(d)
		self.num = ''
		self.dontquit = True
		self.string = False
		self.ended = False
		self.sleep = False
		self.skip = None
		self.keyrecord = False
		self.pause = False
		self.tick = 0
		self.lasttick = 0

	def move(self, times=1, pos=None, dir=None):
		if pos == None:
			pos = self.pos
		if dir == None:
			dir = self.dir
		for _ in range(times):
			if dir > 1:
				a = -1
			else:
				a = 1
			c = dir % 2
			pos[c] += a
			if pos[c] < 0:
				pos[c] = self.size[c] - (-pos[c] % self.size[c])
			else:
				pos[c] %= self.size[c]

	def chr(self, pos=None):
		if pos == None:
			pos = self.pos
		cmd = ' '
		if -1 < pos[1] < len(self.source) and -1 < pos[0] < len(self.source[pos[1]]):
			cmd = self.source[pos[1]][pos[0]]
		return cmd

	def set(self, pos, c):
		if -1 < pos[1] < len(self.source) and -1 < pos[0] < self.size:
			w = len(self.source[pos[1]])
			if pos[0] == w:
				self.source[pos[1]] += c
			elif pos[0] > w:
				self.source[pos[1]] += ' ' * (pos[0] - w) + c
			else:
				l = self.source[pos[1]]
				self.source[pos[1]] = l[:pos[0]] + c + l[pos[0]+1:]

	def next(self, full=True, cont=True):
		cmd = self.chr()
		d = ['>','v','<','^',' ','\\','/']
		if cont and cmd in d:
			while cmd in d:
				self.do(cmd)
				cmd = self.next(False,False)
		if not full or cmd in digits + ',.-"#':
			return cmd
		self.move()
		r = [cmd,self.next(False)]
		self.move()
		return r

	def goto(self, x, y, d=None):
		if d != None:
			self.dir = d
		self.pos = [x % self.size[0],y % self.size[1]]

	def do(self, sect, cmd=''):
		self.tick += 1
		if sect != ' ' or cmd:
			debug.p('sect: %s cmd: %s pos: %s' % (sect,cmd,self.pos))
		if not cmd:
			d = ['>','v','<','^']
			if sect in d + ['\\','/']:
				if sect in d:
					self.dir = d.index(sect)
				elif sect == '\\':
					if self.dir % 2:
						self.dir -= 1
					else:
						self.dir += 1
				elif sect == '/':
					self.dir = 3 - self.dir
			elif sect == '"':
				self.data.push(0)
				self.string = True
			elif sect in '-.' + digits:
				self.num = sect
			#Jump next 2 characters (made for use with flow controll)
			elif sect == ',':
				self.move(2)
			self.move()
		#Push next cmds ascii
		elif sect == "'":
			self.data.push(ord(cmd))
		#Stack
		elif sect == 's':
			#Increase stack pointer
			if cmd == '+':
				self.data.stack += 1
			#Decrease stack pointer
			elif cmd == '-':
				self.data.stack -= 1
			#Increase/Decrease stack pointer by pop
			elif cmd == '*':
				self.data.stack += self.data.pop(t=int)
			#Zero the stack
			elif cmd == 'Z':
				self.data.set([])
			#Pop and do nothing
			elif cmd == 'd':
				self.data.pop()
			#Pop x, then pop and do nothing x times
			elif cmd == 'D':
				d = self.data.pop(0,self.data.len(),int)
				if d == self.data.len():
					self.data.set([])
				else:
					for _ in range(d):
						self.data.pop()
			#Push the stack pointer onto the stack
			elif cmd == 's':
				self.data.push(self.data.stack)
			#Pop the stack pointer from the stack
			elif cmd == 'S':
				self.data.stack = self.data.pop(t=int)
			#Duplicate peek
			elif cmd == 'y':
				self.data.push(self.data.peek())
			#Pop x, then dublicate pop x times
			elif cmd == 'Y':
				x = self.data.pop(0,t=int)
				if x == 0:
					self.data.pop()
				else:
					self.data.push(x * [self.data.peek()])
			#Dublicate top two pops
			elif cmd == 'w':
				self.data.push(self.data.peek(2))
			#Dublicate top pop pops
			elif cmd == 'W':
				self.data.push(self.data.peek(self.data.pop(1,self.data.len(),int)))
			#Pop x and y, push y then x
			elif cmd == 'f':
				x,y = self.data.pop(),self.data.pop()
				self.data.push([y,x])
			#Push the amount of numbers on the stack
			elif cmd == 'a':
				self.data.push(self.data.len())
			#Pop x, then copy peek to stack x
			elif cmd == 'c':
				s = self.data.pop(t=int)
				self.data.push(self.data.peek(),s)
			#Pop x and y, then copy y numbers to stack x
			elif cmd == 'C':
				s = self.data.pop(t=int)
				self.data.push(self.data.peek(self.data.pop(1,self.data.len(),t=int)),s)
			#Replace all pop with pop
			elif cmd == 'R':
				self.data.replace(self.data.pop(),self.data.pop())
			#Pop and push to stack above
			elif cmd == 'A':
				self.data.push(self.data.pop(),self.data.stack + 1)
			#Pop and push to stack below
			elif cmd == 'B':
				self.data.push(self.data.pop(),self.data.stack - 1)
		#List
		elif sect == 'l':
			#Get number pop in the stack
			if cmd == 'g':
				self.data.push(self.data.get(self.data.pop(1,t=int)))
			#Push index of pop in the stack
			elif cmd == 'i':
				self.data.push(self.data.index(self.data.pop()))
			#Push index pop of pop in the stack
			elif cmd == 'I':
				n = self.data.pop(1,t=int)
				self.data.push(self.data.index(self.data.pop(),n))
			#Pop x, then copy number pop to stack x
			elif cmd == 'c':
				s = self.data.pop(t=int)
				self.data.push(self.data.get(self.data.pop(1,t=int)),s)
			#Pop x and y, then copy y numbers starting from pop to stack x
			elif cmd == 'C':
				s = self.data.pop(t=int)
				a = self.data.pop(1,t=int)
				b = self.data.pop(1,t=int)
				self.data.push(self.data.get(b,a),s)
			#Remove all occurences of pop
			elif cmd == 'r':
				self.data.remove(self.data.pop(),-1)
			#Remove pop occurences of pop
			elif cmd == 'R':
				a = self.data.pop(t=int)
				self.data.remove(self.data.pop(),a)
			#Pop x, swap pop with number x
			elif cmd == 'f':
				p = self.data.pop(2,t=int)
				a = self.data.get(1,p)
				a = a[-1:] + a[1:-1] + a[:1]
				a.reverse()
				if p < self.data.len():
					s = self.data.get(p + 1,self.data.len() - p)
					s.reverse()
					a = s + a
				self.data.set(a)
			#Pop x, set item x to pop
			elif cmd == 's':
				s = self.data.pop(t=int)
				v = self.data.pop()
				if s > 0:
					t = self.data.data.get(self.data.stack,[])
					if len(t) < s:
						t = [0] * (s - len(t)) + t
					t[-s] = v
					self.data.set(t)
		#String
		elif sect == 'S':
			#Reverse string
			if cmd == 'r':
				self.data.push([ord(c) for c in reversed(self.data.string())] + [0])
			#Delete string
			elif cmd == 'd':
				self.data.string()
			#Copy string
			elif cmd == 'y':
				s = [ord(c) for c in self.data.string()] + [0]
				self.data.push(s*2)
			#Pop x then copy string x times
			elif cmd == 'Y':
				x = self.data.pop(0,t=int)
				s = [ord(c) for c in self.data.string()] + [0]
				self.data.push(s*x)
			#Pop x, then copy string to stack x
			elif cmd == 'c':
				x = self.data.pop(t=int)
				s = [ord(c) for c in self.data.string()] + [0]
				self.data.push(s)
				self.data.push(s,x)
			#Copy top two strings
			elif cmd == 'w':
				string = [ord(c) for c in self.data.string()] + [0]
				string2 = [ord(c) for c in self.data.string()] + [0]
				for _ in range(2):
					self.data.push(string2)
					self.data.push(string)
			#Remove the seperator for the string
			elif cmd == 'Z':
				self.data.push([ord(c) for c in self.data.string()])
			#Push the height then width of string
			elif cmd == 's':
				self.data.push(list(self.d.size(self.data.string())))
			#Turn a number into a string
			elif cmd == 'S':
				s = [ord(c) for c in str(self.data.pop())] + [0]
				self.data.push(s)
			#Turn a string into a number
			elif cmd == 'N':
				s = self.data.string()
				try:
					if '.' in s:
						self.data.push(float(s))
					else:
						self.data.push(int(s))
				except:
					self.data.push(0)
			#Replace all of pop with pop in string
			elif cmd == 'R':
				rep = chr(self.data.pop(0,255,t=int))
				rwith = chr(self.data.pop(0,255,t=int))
				self.data.push([ord(c) for c in self.data.string().replace(rep,rwith)] + [0])
		#Flow
		elif sect == 'F':
			#End program
			if cmd == 'e':
				pygame.display.set_caption(pygame.display.get_caption()[0] + ' [Complete]')
				if debug.on:
					 debug.toggle()
				self.ended = True
			#If pop is zero, jump the next command
			elif cmd == '?':
				if not self.data.pop():
					self.move()
			#If pop is not negative, jump next command
			elif cmd == '!':
				if self.data.pop() > -1:
					self.move()
			#If pop != pop, jump the next command
			elif cmd == '=':
				if self.data.pop() != self.data.pop():
					self.move()
			#If pop,pop != pop,pop jump the next command
			elif cmd == 'E':
				if [self.data.pop(),self.data.pop()] != [self.data.pop(),self.data.pop()]:
					self.move()
			#If string != string jump the next command
			elif cmd == 'S':
				if self.data.string() != self.data.string():
					self.move()
			#If pop > pop, jump the next command
			elif cmd == 'G':
				n1 = self.data.pop()
				n2 = self.data.pop()
				debug.p('Greater: %s > %s' % (n1,n2),on=True)
				if n1 > n2:
					self.move()
			#Jump next command
			elif cmd == 'j':
				self.move()
			#Jump next pop commands
			elif cmd == 'J':
				for _ in range(self.data.pop(2,t=int)):
					self.move()
			#Skip till character pop is found
			elif cmd == 's':
				self.skip = self.data.pop(0,t=int) % 256
			#Go to the begining of the current line and go right
			elif cmd == 'b':
				self.pos[0] = 0
				self.dir = 0
			#Go to the begining of the next line of code and go right
			elif cmd == 'n':
				self.pos = [0,(self.pos[1] + 1) % self.size[1]]
				self.dir = 0
			#Go to the begining of the previous line of code and go right
			elif cmd == 'p':
				if self.pos[1] == 0: self.pos[1] = self.size[1]
				else: self.pos[1] = self.pos[1] - 1
				self.pos[0] = 0
				self.dir = 0
			#Go to command at pop,pop
			elif cmd == 'g':
				self.goto(self.data.pop(0,t=int),self.data.pop(0,t=int))
		#Output
		elif sect == 'O':
			if cmd in 'nNcCsS':
				bg = None
				bitmask = self.data.graph(7)
				if bitmask & 4:
					bg = self.data.graph(4)
				#Output pop as a number
				if cmd in 'nN':
					self.d.write(self.data.pop(t=str), self.data.graph(3), self.data.graph(0), bg)
				#Output pop as a character
				elif cmd in 'cC':
					self.d.write(chr(self.data.pop(0,t=int) % 256), self.data.graph(3), self.data.graph(0), bg)
				#Output a string
				elif cmd in 'sS':
					self.d.write(self.data.string(), self.data.graph(3), self.data.graph(0), bg)
				#Output and push the y then x of the lines end
				if cmd in 'NCS':
					self.data.push(list(self.d.contline))
		#Input
		elif sect == 'I':
			#Input a string - Input a character
			if cmd in 'sSc':
				bg = None
				bitmask = self.data.graph(7)
				if bitmask & 4:
					bg = self.data.graph(4)
				l = 0
				if cmd == 'c':
					l = 1
				elif cmd == 'S':
					l = self.data.pop(0,t=int)
				s = self.d.get(self.data.graph(3), self.data.graph(0), l, bg)
				if s:
					self.data.push([ord(x) for x in s])
				else:
					self.data.push(0)
			#Input a number
			elif cmd in 'nN':
				bg = None
				bitmask = self.data.graph(7)
				if bitmask & 4:
					bg = self.data.graph(4)
				l = 0
				if cmd == 'N':
					l = self.data.pop(0,t=int)
				s = self.d.get(self.data.graph(3), self.data.graph(0), l, bg, 2)
				if s:
					self.data.push(s)
				else:
					self.data.push(0)
		#Display/Drawing
		elif sect == 'D':
			#Refresh the screen
			if cmd == 'r':
				self.d.refresh()
			#Change resolution to pop,pop
			elif cmd == 'R':
				self.d.res = (self.data.pop(100,1024,int),self.data.pop(100,1024,int))
				self.d.newscreen()
			#Set to fullscreen
			elif cmd == 'f':
				self.d.newscreen(True)
			#Clear the screen(all layers)
			elif cmd == 'c':
				self.d.clear()
			#Copy a part of the screen to pop x,y
			elif cmd == 'C':
				self.d.copy(self.data.graph(0),self.data.graph(1),self.data.graph(2))
			#Draw a point/circle
			elif cmd == 'p':
				#bitmask = self.data.graph(7)
				#bitmask = self.data.graph(7)
				#if bitmask & 2:
				#	self.d.point(self.data.graph(4), self.data.graph(0), r)
				#w = 0
				#if bitmask & 2 or not bitmask & 1:
				#	w = self.data.graph(6)
				self.d.point(self.data.graph(3), self.data.graph(0)) #, r, w)
			#Draw a box
			elif cmd == 'b':
				tl, br = self.data.graph(0),self.data.graph(1)
				r = pygame.Rect(tl,(br[0] - tl[0],br[1] - tl[1]))
				r.normalize()
				bitmask = self.data.graph(7)
				if bitmask & 2:
					self.d.rect(self.data.graph(4), r)
				w = 0
				if bitmask & 2 or not bitmask & 1:
					w = self.data.graph(6)
				self.d.rect(self.data.graph(3), r, w)
			#Draw a line
			elif cmd == 'l':
				self.d.line(self.data.graph(3), self.data.graph(0), self.data.graph(1), self.data.graph(6))
			#Push width of screen
			elif cmd == 'w':
				self.data.push(self.d.res[0])
			#Push height of screen
			elif cmd == 'h':
				self.data.push(self.d.res[1])
			#Push the stack pointer of graphics setting pop
			elif cmd == 'g':
				self.data.push(self.data.graphics[self.data.pop(0,6,t=int)])
			#Set graphics setting pop to pop
			elif cmd == 'G':
				setting = self.data.pop(0,7,t=int)
				stack = self.data.pop(t=int)
				self.data.graphics[setting] = stack
				debug.p('Graphics: ' + repr(self.data.graphics),on=True)
			#Get the pressed status of key pop
			elif cmd == 'k':
				if self.data.pop(8,321,int) in self.data.keys:
					self.data.push(1)
				else:
					self.data.push(0)
			#Push titlebar text as string
			elif cmd == 't':
				self.data.push([ord(c) for c in pygame.display.get_caption()[0]] + [0])
			#Set titlebar text to a string
			elif cmd == 'T':
				pygame.display.set_caption(self.data.string())
		#Fonts
		elif sect == 'T':
			#Increase font pointer
			if cmd == '+':
				self.d.font += 1
				self.d.font %= len(self.d.fonts)
			#Decrease font pointer
			elif cmd == '-':
				if self.d.font == 0 :
					self.d.font = len(self.d.font) - 1
				else:
					self.d.font -= 1
			#Push font pointer to stack
			elif cmd == 'l':
				self.data.push(self.d.font)
			#Set font pointer to pop
			elif cmd == 'L':
				self.d.font = self.data.pop(0,len(self.d.fonts) - 1,int)
			#Flip top two fonts
			elif cmd == 'f':
				if len(self.d.fonts) > 1:
					self.d.fonts[-2:] = self.d.fonts[-1] + self.d.fonts[-2]
			#Flip top font with font pop
			elif cmd == 'F':
				if len(self.d.fonts) > 1:
					f = self.data.pop(1,len(self.d.fonts) - 1,int)
					s = self.d.fonts[f]
					self.d.fonts[f] = self.d.fonts[-1]
					self.d.fonts[-1] = s
			#New font
			elif cmd == 'n':
				n = self.data.string()
				if n == '':
					n = 'lucon.ttf'
				s = self.data.pop(6,t=int)
				self.d.fonts(pygame.font.Font(n, s))
				self.data.push(len(self.d.fonts) - 1)
			#Delete current font(except for font 0)
			elif cmd == 'd':
				if self.d.font != 0:
					del self.d.fonts[self.d.font]
			#Delete pop fonts starting from current font
			elif cmd == 'd':
				a = self.data.pop(0,len(self.d.fonts) - self.d.font)
				if self.d.font - a > 0:
					p = len(self.d.fonts) - self.d.font + 1
					del self.d.fonts[p - a,p]
		#Layers
		elif sect == 'l':
			#Increase layer pointer
			if cmd == '+':
				self.d.layer += 1
				self.d.layer %= len(self.d.layers)
			#Decrease layer pointer
			elif cmd == '-':
				if self.d.layer == 0 :
					self.d.layer = len(self.d.layers) - 1
				else:
					self.d.layer -= 1
			#Push amount of layers on stack
			elif cmd == 'a':
				self.data.push(len(self.d.layers))
			#Push layer pointer to stack
			elif cmd == 'l':
				self.data.push(self.d.layer)
			#Set layer pointer to pop
			elif cmd == 'L':
				self.d.layer = self.data.pop(0,len(self.d.layers) - 1,int)
			#Flip top two layers
			elif cmd == 'f':
				if len(self.d.layers) > 1:
					self.d.layers[-2:] = self.d.layers[-1] + self.d.layers[-2]
			#Flip top layer with layer pop
			elif cmd == 'F':
				if len(self.d.layers) > 1:
					f = self.data.pop(1,len(self.d.layers) - 1,int)
					s = self.d.layers[f]
					self.d.layers[f] = self.d.layers[-1]
					self.d.layers[-1] = s
			#Push transparency to stack
			elif cmd == 't':
				self.data.push(list(self.d.layers[self.d.layer].get_colorkey()))
			#Set transparency for layer to pop,pop,pop
			elif cmd == 'T':
				self.d.layers[self.d.layer].set_colorkey((self.data.pop(0,255,int),self.data.pop(0,255,int),self.data.pop(0,255,int)))
			#Clear current layer
			elif cmd == 'c':
				self.d.clear(self.d.layer)
			#New layer
			elif cmd == 'n':
				self.d.newlayer()
			#Delete current layer(except for layer 0)
			elif cmd == 'd':
				if self.d.layer != 0:
					del self.d.layers[self.d.layer]
			#Delete pop layers starting from current layer
			elif cmd == 'd':
				a = self.data.pop(0,len(self.d.layers) - self.d.layer)
				if self.d.layer - a > 0:
					p = len(self.d.layers) - self.d.layer + 1
					del self.d.layers[p - a,p]
		#Keyboard
		elif sect == 'K':
			#Sleep till keypress
			if cmd == 's':
				debug.p(repr(self.data.data),on=True)
				debug.p(repr(self.data.graphics),on=True)
				self.sleep = True
			#Record keypresses
			elif cmd == 'r':
				self.keyrecord = True
			#Push top keypress from keyrecord
			elif cmd == 'n':
				self.data.push(self.data.key())
			#Push keypresses from keyrecord
			elif cmd == 'p':
				if not self.data.keyrecord:
					self.data.push(0)
				else:
					self.data.push(self.data.keyrecord)
					self.data.keypump()
			#Clear keypresses from keyrecord
			elif cmd == 'c':
				self.data.keypump()
			#Stop recording keypresses
			elif cmd == 'S':
				self.keyrecord = False
				self.data.keypump()
		#Math
		elif sect == 'M':
			#Pop x, push x + 1
			if cmd == 'i':
				self.data.push(self.data.pop() + 1)
			#Pop x, push x - 1
			elif cmd == 'd':
				self.data.push(self.data.pop() - 1)
			#Push pop + pop
			elif cmd == '+':
				self.data.push(self.data.pop() + self.data.pop())
			#Push pop - pop
			elif cmd == '-':
				self.data.push(self.data.pop() - self.data.pop())
			#Push pop * pop
			elif cmd == '*':
				self.data.push(self.data.pop() * self.data.pop())
			#Push pop / pop
			elif cmd == '_':
				self.data.push(self.data.pop() / self.data.pop(t=float))
			#Push pop % pop
			elif cmd == '%':
				self.data.push(self.data.pop() % self.data.pop())
			#Push pop ^ pop
			elif cmd == '^':
				self.data.push(self.data.pop() ** self.data.pop())
			#Push the square root of pop
			elif cmd == '~':
				self.data.push(math.sqrt(self.data.pop()))
			#Pop x and push x as an integer(remove anything after the .)
			elif cmd == 'I':
				self.data.push(self.data.pop(t=int))
			#Push a random number from 0 to 1
			elif cmd == 'r':
				self.data.push(random.random())
			#Push a random number from pop to pop
			elif cmd == 'R':
				s = self.data.pop()
				self.data.push(s + random.random() * (self.data.pop() - s))
			#Push the sin of pop
			elif cmd == 's':
				self.data.push(math.sin(self.data.pop()))
			#Push the arcsin of pop
			elif cmd == 'S':
				self.data.push(math.asin(self.data.pop(-1,1)))
			#Push the cos of pop
			elif cmd == 'c':
				self.data.push(math.cos(self.data.pop()))
			#Push the arccos of pop
			elif cmd == 'C':
				self.data.push(math.acos(self.data.pop(-1,1)))
			#Push the tan of pop
			elif cmd == 't':
				self.data.push(math.tan(self.data.pop()))
			#Push the arctan of pop
			elif cmd == 'T':
				self.data.push(math.cos(self.data.pop(-1,1)))
			#Push pop in radians
			elif cmd == 'Q':
				self.data.push(math.radians(self.data.pop()))
			#Push pop in degrees
			elif cmd == 'D':
				self.data.push(math.degrees(self.data.pop()))
			#Negate top value
			elif cmd == 'n':
				self.data.push(-self.data.pop())
		#Logic
		elif sect == 'L':
			#Bitwise and
			if cmd == '&':
				self.data.push(self.data.pop(t=int) & self.data.pop(t=int))
			#Bitwise or
			elif cmd == '|':
				self.data.push(self.data.pop(t=int) | self.data.pop(t=int))
			#Bitwise xor
			elif cmd == 'X':
				self.data.push(self.data.pop(t=int) ^ self.data.pop(t=int))
			#Logical not
			elif cmd == '!':
				if self.data.pop():
					self.data.push(0)
				else:
					self.data.push(1)
		#File
		elif sect == 'f':
			#Increase filepointer
			if cmd == '+':
				self.data.file += 1
				self.data.file %= len(self.data.files)
			#Decrease file pointer
			elif cmd == '-':
				if self.data.file == 0 :
					self.data.file = len(self.data.files) - 1
				else:
					self.data.file -= 1
			#Open a file for reading or writing
			elif cmd in 'WR':
				try:
					file = self.data.string()
					#print 'Open: ' + fullfile(file)
					self.data.files.append(open(fullfile(file),{'W':'w','R':'r'}[cmd]))
					self.data.file = len(self.data.files) - 1
					self.data.push(self.data.file)
				except:
					self.data.push(-1)
			#Push next ascii from the file
			elif cmd == 'r':
				self.data.push(self.data.read())
			#Read the remaining characters from the file
			elif cmd == 'a':
				self.data.push(self.data.read(0))
			#Close the file
			elif cmd == 'C':
				self.data.close()
			#Write a chr to the file
			elif cmd == 'c':
				self.data.write(chr(self.data.pop(1,t=int) % 256))
			#Write a string to the file
			elif cmd == 's':
				self.data.write(self.data.string())
			#Write a number to the file
			elif cmd == 'n':
				self.data.write(self.data.pop(t=str))
		#Custom command creating
		elif sect == 'c':
			#Set custom command to (pop,pop) with direction pop
			if cmd != 'R':
				self.data.commands[cmd] = [self.data.pop(0,self.size[0],int),self.data.pop(0,self.size[1],int),self.data.pop(0,3,int)]
		#Custom commands
		elif sect == 'C':
			#Return to position and direction before custom command
			if cmd == 'R':
				self.goto(*self.data.cmdreturn[-1])
				if len(self.data.cmdreturn) > 1:
					self.data.cmdreturn.pop()
			elif cmd in self.data.commands:
				self.data.cmdreturn.append(list(self.pos) + [self.dir])
				self.goto(*self.data.commands[cmd])
		#Misc commands
		elif sect == 'm':
			#Push ticks since program start
			if cmd == 't':
				self.data.push(self.tick)
				self.lasttick = self.tick
			#Push ticks since last mt or mT
			elif cmd == 'T':
				self.data.push(self.tick - self.lasttick)
				self.lasttick = self.tick
			#Toggle debug output
			elif cmd == 'D':
				debug.toggle()
		#Socket commands
		elif sect == 'i':
			#Increase socket pointer
			if cmd == '+':
				self.data.socket += 1
				self.data.socket %= len(self.data.sockets)
			#Decrease socket pointer
			elif cmd == '-':
				if self.data.socket == 0 :
					self.data.socket = len(self.data.sockets) - 1
				else:
					self.data.socket -= 1
			#Connect to socket with port pop and ip string
			elif cmd in 'cC':
				port = self.data.pop(t=int)
				if 0 >= port or port >= 65536:
					self.data.push(-1)
				else:
					#Pop read size for C
					if cmd == 'C':
						self.data.push(self.data.sockopen(self.data.string(), port, self.data.pop(t=int)))
					else:
						self.data.push(self.data.sockopen(self.data.string(), port))
			#Start a listen socket
			elif cmd in 'lL':
				port = self.data.pop(t=int)
				if 0 >= port or port >= 65536:
					self.data.push(-1)
				else:
					#Pop read size and max queue for L
					if cmd == 'L':
						self.data.push(self.data.listen(port, self.data.pop(t=int), self.data.pop(t=int)))
					else:
						self.data.push(self.data.listen(port))
			#Check the status of a socket
			elif cmd == 's':
				self.data.push(self.data.sockets[self.data.socket].status)
			#Send data to a socket
			elif cmd == 'S':
				self.data.send(self.data.string())
			#Read pop bytes for a socket
			elif cmd == 'r':
				self.data.push(self.data.readbytes(self.data.pop(t=int)))
			#Read up to a delimeter string
			elif cmd == 'R':
				self.data.push(self.data.readupto(self.data.string()))
		#Regular Expressions
		elif sect == 'R':
			#Checks if pattern string matches string
			if cmd == 'm':
				try:
					if re.match(self.data.string(),self.data.string()):
						self.data.push(1)
					else:
						self.data.push(0)
				except:
					self.data.push(0)
			#Replace all non-overlapping matches of pattern string with replace string in string
			elif cmd == 'r':
				pattern = self.data.string()
				rep = self.data.string()
				text = self.data.string()
				debug.p('P: %s R: %s T: %s' % (repr(pattern), repr(rep), repr(text)),on=True)
				try:
					self.data.push([ord(c) for c in re.sub(pattern, rep, text)] + [0])
				except:
					self.data.push([ord(c) for c in text] + [0])
		#Source manipulation
		elif sect == 'Q':
			#Pop x then y, Push ascii of character at position x,y in source
			if cmd == 'g':
				self.data.push(ord(self.chr([self.data.pop(t=int),self.data.pop(t=int)])))
			#Pop x, y, then d, Push asciis of command at position x,y going in direction d % 4. command ascii pushed first, section second
			elif cmd == 'G':
				pos = [self.data.pop(t=int),self.data.pop(t=int)]
				sect = ord(self.chr(pos))
				self.move(pos,self.data.pop(0, t=int) % 4)
				self.data.push([ord(self.chr(pos)),sect])
			#Pop c, x, then y, set character at position x,y in source to character with ascii value c % 255 + 1
			elif cmd == 'c':
				c = chr(self.data.pop(0,t=int) % 255 + 1)
				self.set([self.data.pop(t=int),self.data.pop(t=int)],c)
			#Pop s, c, x, y then d, set command at position x,y going in direction d % 4, to section s and command c, both % 255 + 1
			elif cmd == 'C':
				s = chr(self.data.pop(0,t=int) % 255 + 1)
				c = chr(self.data.pop(0,t=int) % 255 + 1)
				pos = [self.data.pop(t=int),self.data.pop(t=int)]
				self.set(pos,s)
				self.move(pos,self.data.pop(0,t=int) % 4)
				self.set(pos,c)
			#Push the height then width of the source
			elif cmd == 's':
				self.data.push(self.size)
		#Variable setting
		elif sect == 'h':
			self.data.variables[cmd] = self.data.pop()
		#Variable getting
		elif sect == 'H':
			self.data.push(self.data.variables.get(cmd,0))

	def execute(self):
		if DEBUG:
			debug.toggle(DEBUG)
		while self.dontquit:
			for event in pygame.event.get():
				if event.type == KEYDOWN:
					if event.key == K_BREAK or event.key == K_PAUSE:
						self.pause = not self.pause
						if self.pause:
							pygame.display.set_caption(pygame.display.get_caption()[0] + ' [Paused]')
						else:
							pygame.display.set_caption(' '.join(pygame.display.get_caption()[0].split(' ')[:-1]))
					elif event.key == K_INSERT:
						self.d.newscreen(True)
					elif (event.key == K_ESCAPE and self.pause) or (event.key == K_RETURN and self.ended):
						debug.p(repr(self.data.data),on=True)
						debug.p(repr(self.data.graphics),on=True)
						return
					if self.sleep:
						self.sleep = False
					if self.keyrecord:
						self.data.keyrecord.append(event.key)
					self.data.keys.append(event.key)
				elif event.type == KEYUP:
					try:
						self.data.keys.remove(event.key)
					except:
						pass
				elif event.type == QUIT:
					debug.p(repr(self.data.data),on=True)
					debug.p(repr(self.data.graphics),on=True)
					sys.exit()
				elif event.type == MOUSEBUTTONDOWN:
					self.data.mouse[min(1,3 - event.button)] = 1
				elif event.type == MOUSEBUTTONUP:
					self.data.mouse[min(1,3 - event.button)] = 0
			if not self.ended and not self.sleep and not self.pause:
				debug.p('     Stack %s: %s' % (self.data.stack, self.data.data.get(self.data.stack,[])))
				if self.string:
					c = self.next(False,False)
					debug.p('  cmd: %s pos: %s' % (c,self.pos))
					if c == '"':
						self.move()
						n = self.next(False,False)
						if n in ['>','v','<','^','\\','/']:
							self.do(n)
						elif n == '"':
							self.data.push(34)
							self.move()
						elif n == 'j':
							self.move(2)
						elif n == 'J':
							self.move(self.data.pop(1,t=int) + 1)
						else:
							self.string = False
					else:
						self.data.push(ord(c))
						self.move()
				elif self.skip:
					c = self.next(False,False)
					if ord(c) == self.skip:
						self.skip = None
						#self.move(dir=(self.dir + 2) % 4)
					else:
						debug.p('  skip: %s pos: %s ascii: %s found: %s' % (c,self.pos,self.skip,ord(c)))
						self.move()
				elif self.num:
					c = self.next(False)
					if c in digits or (c == '.' and not '.' in self.num and self.num[-1] in digits):
						self.num += c
						self.move()
					elif c in ['>','v','<','^','\\','/',' ']:
						self.do(c)
						self.move()
					else:
						if self.num != '-' and self.num != '.':
							self.data.push(float(self.num))
						self.num = ''
				else:
					cmd = self.next()
					self.do(*cmd)
		debug.close()
