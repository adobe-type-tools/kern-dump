import sys, re

'''

Takes feature file, returns python KerningClass class for each kern class found within that file.
KerningClass object has .glyphs, .side, .name options.

'''

def readFile(filePath):
	file = open(filePath, 'r')
	fileLinesString = file.read()
	file.close()
	return fileLinesString

class KerningClass(object):
	def __init__(self):
		self.glyphs = []
		self.name = ''
		self.side = ''

kernClassesString = readFile(sys.argv[1])

allClassesList = re.findall(r"@(\S+)\s*=\s*\[([ A-Za-z0-9_.]+)\]\s*;", kernClassesString)

classes = []
for name, glyphs in allClassesList:
	c = KerningClass()
	c.name = name
	c.glyphs = glyphs.split()

	if name.split('_')[-1] == 'LEFT':
		c.side = 'LEFT'
		classes.append(c)
	elif name.split('_')[-1] == 'RIGHT':
		c.side = 'RIGHT'
		classes.append(c)
	else:
		c.side = 'LEFT'
		classes.append(c)

		d = KerningClass()
		d.name = c.name
		d.glyphs = c.glyphs
		d.side = 'RIGHT'
		classes.append(d)
		

for i in classes:
	print i.name, i.side, i.glyphs