from Zetaplex import fullfile
import pygame, sys
from pygame.locals import *

DEFAULT_RES = (600,320)
CENTER_SCREEN = (DEFAULT_RES[0] / 2, DEFAULT_RES[1] / 2)

class Display:
	def __init__(self):
		self.mode = 0
		self.res = DEFAULT_RES
		self.layers = []
		self.layer = 0
		self.newscreen()
		self.layers.append(pygame.Surface(self.screen.get_size()).convert())
		self.layers[0].set_colorkey(None)
		pygame.display.set_caption('Zetaplex')
		self.clear()
		self.refresh()
		try:
			self.fonts = [pygame.font.Font(fullfile('lucon.ttf'), 12)]
		except:
			self.fonts = [pygame.font.Font(None, 12)]
		self.font = 0

	def newlayer(self):
		d = pygame.Surface(self.screen.get_size()).convert()
		d.set_colorkey((0,0,0))
		self.layers.append(d)

	def clear(self, layer=None):
		if layer == None:
			self.layers[0].fill((0,0,0))
			for layer in self.layers[1:]:
				layer.fill(layer.get_colorkey())
		elif layer == 0:
			self.layers[0].fill((0,0,0))
		else:
			self.layers[layer].fill(self.layers[layer].get_colorkey())

	def refresh(self):
		for layer in self.layers:
			self.screen.blit(layer, (0,0))
		pygame.display.flip()

	def point(self, color, pos, layer=None):
		if layer == None:
			layer = self.layer
		self.layers[layer].set_at(pos,color)

	def rect(self, color, rect, width=0, layer=None):
		if layer == None:
			layer = self.layer
		pygame.draw.rect(self.layers[layer], color, rect, width)

	def line(self, color, start, end, width, layer=None):
		if layer == None:
			layer = self.layer
		pygame.draw.line(self.layers[layer], color, start, end, width)

	def size(self, text):
		return self.fonts[self.font].size(text)

	def write(self, text, color, pos, bg=None, layer=None):
		if layer == None:
			layer = self.layer
		if bg:
			self.layers[layer].blit(self.fonts[self.font].render(text, 1, color, bg), pos)
		else:
			self.layers[layer].blit(self.fonts[self.font].render(text, 1, color), pos)
		self.newline = (pos[0], pos[1] + self.fonts[self.font].get_linesize())
		self.contline = (pos[0] + self.fonts[self.font].size(text)[0], pos[1])

	# type 1 is alpha only, type 2 is number only
	def get(self, color, pos, maxlen=0, bg=None, type=0):
		self.newlayer()
		o = self.layers[-1]
		def showinput():
			o.fill((0,0,0))
			if bg:
				o.blit(self.fonts[self.font].render(text, 1, color, bg), pos)
			else:
				o.blit(self.fonts[self.font].render(text, 1, color), pos)
			self.refresh()
		text = ''
		cont = True
		while cont:
			for event in pygame.event.get():
				if event.type == KEYDOWN:
					k = range(32,127)
					if event.key in k and event.unicode and ord(event.unicode) in k and (maxlen == 0 or len(text) < maxlen):
						text += event.unicode
						showinput()
					elif event.key == K_BACKSPACE:
						text = text[0:-1]
						showinput()
					elif event.key == K_RETURN:
						if type != 2:
							text += chr(0)
						cont = False
						break
					elif event.key == K_INSERT:
						self.newscreen(True)
					elif event.key == K_ESCAPE:
						text = False
						cont = False
						break
				elif event.type == QUIT:
					sys.exit()
		self.layers.pop()
		if type == 2:
			try:
				return int(text)
			except:
				return 0
		return text

	def newscreen(self, changemode=False):
		if changemode and self.mode == 0:
			self.mode = pygame.FULLSCREEN
		else:
			self.mode = 0
		self.screen = pygame.display.set_mode(self.res, self.mode)
		for n,layer in enumerate(self.layers):
			l = layer.copy()
			self.layers[n] = pygame.Surface(self.screen.get_size()).convert()
			self.layers[n].set_colorkey(l.get_colorkey())
			self.clear(n)
			self.layers[n].blit(l, (0,0))
		self.refresh()

	def copy(self, topleft, botright, dest, layer=None):
		if layer == None:
			layer = self.layer
		self.layers[layer].blit(self.layers[layer].copy(), dest, (topleft,botright))
