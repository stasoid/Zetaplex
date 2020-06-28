import pygame, os, sys
import disp, interp
from pygame.locals import *

version = (-1,0,0)
long_version = 'v%s.%s.%s' % version

WHITE = (255,255,255)
GRAY = (100,100,100)
BASE = os.path.dirname(__file__)

def fullfile(file):
	return os.path.join(BASE, file)

class MenuSystem:
	def interpretscreen(self):
		s = self.d.size('Interpret')
		h = 2 + s[1]
		x = 2
		file = ''
		while not file:
			self.d.clear()
			self.d.write('Interpret', WHITE, (disp.CENTER_SCREEN[0] - s[0] / 2,2))
			if x == 3:
				self.d.write('Invalid program!', (255,0,0), (2,h * 2))
			self.d.write('Code filename: ', WHITE, (2, h * x))
			i = self.d.contline
			self.d.write('Note: Do not include .zeta', GRAY, (2, h * (x + 1)))
			t = 'Press ESC to return to Main Menu'
			q = self.d.size(t)
			self.d.write(t, GRAY, (disp.CENTER_SCREEN[0] - q[0] / 2, disp.DEFAULT_RES[1] - 2 - q[1]))
			self.d.refresh()
			get = self.d.get(WHITE, i)
			if get == False:
				return
			file = fullfile('%s%szeta' % (get[:-1], os.extsep))
			if not os.path.isfile(file):
				file = ''
				if x == 2:
					x += 1
		source = [line.rstrip('\r\n') for line in open(file, 'U').readlines()]
		e = interp.Interpreter(self.d, source)
		e.execute()
		if self.d.res != disp.DEFAULT_RES:
			self.d.res = disp.DEFAULT_RES
			self.d.newscreen()
		if pygame.display.get_caption()[0] != 'Zetaplex':
			pygame.display.set_caption('Zetaplex')

	def compilescreen(self):
		s = self.d.size('Compile')
		h = 2 + s[1]
		x = 2
		file = ''
		while not file:
			self.d.clear()
			self.d.write('Compile', WHITE, (disp.CENTER_SCREEN[0] - s[0] / 2,2))
			if x == 3:
				self.d.write('Invalid program!', (255,0,0), (2,h * 2))
			self.d.write('Code filename: ', WHITE, (2, h * x))
			i = self.d.contline
			self.d.write('Note: Do not include .zeta', GRAY, (2, h * (x + 1)))
			t = 'Press ESC to return to Main Menu'
			q = self.d.size(t)
			self.d.write(t, GRAY, (disp.CENTER_SCREEN[0] - q[0] / 2, disp.DEFAULT_RES[1] - 2 - q[1]))
			self.d.refresh()
			get = self.d.get(WHITE, i)
			if get == False:
				return
			file = fullfile('%s%szeta' % (get[:-1], os.extsep))
			if not os.path.isfile(file):
				file = ''
				if x == 2:
					x = 3
		comp.compile(get[:-1])

	def aboutscreen(self):
		skip = False
		def events():
			for event in pygame.event.get():
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						return True
					elif event.key == K_INSERT:
						self.d.newscreen(True)
					elif event.key == K_RETURN:
						skip = True
				elif event.type == QUIT:
					self.exitscreen()
			return False
		self.d.clear()
		s = self.d.size('About')
		self.d.write('About', WHITE, (disp.CENTER_SCREEN[0] - s[0] / 2, 2))
		t = 'Press ESC to return to Main Menu'
		q = self.d.size(t)
		self.d.write(t, GRAY, (disp.CENTER_SCREEN[0] - q[0] / 2, disp.DEFAULT_RES[1] - 2 - q[1]))
		y = 6 + s[1] * 3
		text = ['This is Zetaplex %s by:' % long_version,'Zach Zahos (poiuy_qwert)','','Thanks to the creator of Gammaplex:','Lode Vandevenne','','Thanks to everyone who worked on pygame,','specifically the creator:','Pete Shinners','','Thanks to the creators of Python:','Python Software Foundation','and its initial creator:','Guido van Rossum']
		for line in text:
			if line:
				s = self.d.size(line)
				x = disp.CENTER_SCREEN[0] - s[0] / 2
				for chr in line:
					self.d.write(chr, WHITE, (x, y))
					self.d.refresh()
					x += self.d.size(chr)[0]
					if events():
						return
					if not skip:
						pygame.time.wait(50)
			y += 2 + s[1]
		while True:
			if events():
				return

	def exitscreen(self):
		self.d.clear()
		t = 'Thank you for using Zetaplex!'
		s = self.d.size(t)
		self.d.write(t, WHITE, (disp.CENTER_SCREEN[0] - s[0] / 2, disp.CENTER_SCREEN[1] - s[1] / 2))
		t = 'Press any button to Exit'
		q = self.d.size(t)
		self.d.write(t, GRAY, (disp.CENTER_SCREEN[0] - q[0] / 2, disp.DEFAULT_RES[1] - 2 - q[1]))
		self.d.refresh()
		cont = True
		while cont:
			for event in pygame.event.get():
				if event.type == KEYDOWN or event.type == QUIT:
					cont = False
					break
		sys.exit()

	def mainscreen(self):
		sys.stderr = open('stderr.txt', 'w')
		sys.stdout = sys.stderr
		pygame.init()
		self.d = disp.Display()
		self.d.newscreen()
		s = self.d.size('Main Menu')
		h = 2 + s[1]
		choices = [self.interpretscreen, self.compilescreen, self.aboutscreen]
		while True:
			self.d.clear()
			self.d.write('Main Menu', WHITE, (disp.CENTER_SCREEN[0] - s[0] / 2,2))
			self.d.write('1) Interpret', WHITE, (2, h * 2))
			self.d.write('2) Compile', WHITE, (2, h * 3))
			self.d.write('3) About', WHITE, (2, h * 4))
			t = 'Press ESC to Exit'
			q = self.d.size(t)
			self.d.write(t, GRAY, (disp.CENTER_SCREEN[0] - q[0] / 2, disp.DEFAULT_RES[1] - 2 - q[1]))
			self.d.refresh()
			cont = True
			while cont:
				for event in pygame.event.get():
					if event.type == KEYDOWN:
						if event.key in [49,50,51]:
							choices[event.key - 49]()
							cont = False
							break
						elif event.key == K_ESCAPE:
							self.exitscreen()
						elif event.key == K_INSERT:
							self.newscreen(True)
					elif event.type == QUIT:
						self.exitscreen()
	
if __name__ == '__main__':
	m = MenuSystem()
	m.mainscreen()