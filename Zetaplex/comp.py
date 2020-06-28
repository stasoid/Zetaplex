import sys, os
from Zetaplex import fullfile

def compile(file):
	m = '%s%spy' % (file, os.extsep)
	s = 'setup%spy' % os.extsep
	i = '%s%sico' % (file, os.extsep)
	mf = fullfile('compile\\%s' % m)
	f = open(mf, 'w')
	main = """import pygame, disp, interp, sys

def main():
	sys.stderr = open('stderr.txt', 'w')
	pygame.init()
	d = disp.Display()
	source = %s
	e = interp.Interpreter(d, source)
	e.execute()

if __name__ == '__main__':
	main()""" % repr([line.rstrip('\r\n') for line in open(fullfile('%s%szeta' % (file, os.extsep)), 'U').readlines()])
	f.write(main)
	f.close()
	try:
		import py2exe
		sf = fullfile('compile\\%s' % s)
		f = open(sf, 'w')
		setup = """from distutils.core import setup
import py2exe"""
		if os.path.isfile(fullfile(i)):
			setup += """setup(windows=[{
	'script': '%s',
	'icon_resources': [(0, '%s')]
}])""" % (m, i)
		else:
			setup += """setup(windows=['%s'])""" % m
		f.write(setup)
		f.close()
		sys.argv.append("py2exe")
		execfile(sf)
		os.remove(sf)
	except:
		import compiler
		compiler.compileFile(mf)
	os.remove(mf)