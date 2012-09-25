import os, sys
import time
from modules.fromGPOS import *
import operator
from defcon import Font

	
def outputFile(path, suffix):
 	return '%s.%s' % (os.path.splitext(fontPath)[0], suffix)


def write2file(path, list):
	o = open(path, 'w')
	o.write('\n'.join(list))
	o.close()

def makeMMK(name, side):
	if name[0] == '@' and name[0:3] != '@MMK':
		name = '@MMK_%s_%s' % (side[0], name[1:])
	return name
	
def replaceKerning(ufo, classes, pairs):
	f = Font(ufo)

	f.groups.clear()
	for i in classes:
		i.name = makeMMK(i.name, i.side)

		for g in i.glyphs:
			if not g in f.keys():
				i.glyphs.remove(g)
		if len(i.glyphs) == 0:
			continue
		else:
	  		f.groups[i.name] = i.glyphs

	f.save()
	f.kerning.clear()

	k = dict(zip([(i[0], i[1]) for i in pairs], [int(i[2]) for i in pairs]))
	mmk_k = {} # kerning with MetricsMachine group names

	gng = [] # groups'n'glyphs
	gng.extend(f.keys())
	gng.extend(f.groups.keys())

	for (left, right), value in k.items():
		left = makeMMK(left, 'LEFT')
		right = makeMMK(right, 'RIGHT')
		mmk_k[(left, right)] = value

	for (left, right), value in mmk_k.items():
	 	if left in gng:

			if right in gng:
				continue
			else:
				del mmk_k[left, right]
		else:
			del mmk_k[left, right]

	f.kerning.update(mmk_k)
	f.save()
	
def appendKerning(ufo, classes, pairs):
	f = Font(ufo)

	for i in classes:
		i.name = makeMMK(i.name, i.side)
		for g in i.glyphs:
			if not g in f.keys():
				i.glyphs.remove(g)
		if len(i.glyphs) == 0:
			continue
		else:
			if i.name in f.groups and i.glyphs == f.groups[i.name]:
				continue
	  		else: f.groups[i.name] = i.glyphs
	
	f.save()
	k = dict(zip([(i[0], i[1]) for i in pairs], [int(i[2]) for i in pairs]))
	mmk_k = {} # kerning with MetricsMachine group names
	
	gng = [] # groups'n'glyphs
	gng.extend(f.keys())
	gng.extend(f.groups.keys())
	
	for (left, right), value in k.items():
		left = makeMMK(left, 'LEFT')
		right = makeMMK(right, 'RIGHT')
		mmk_k[(left, right)] = value
	
	for (left, right), value in mmk_k.items():
	 	if left in gng:
			if right in gng:
				continue
			else:
				del mmk_k[left, right]
		else:
			del mmk_k[left, right]
	
	f.kerning.update(mmk_k)
	f.save()
	
	
def stripClasses(ufo):
	f = Font(ufo)
	for name, group in f.groups.items()[::-1]:
		if len(group) == 0:
			del f.groups[name]
	f.save()

def madLib(ufo, orderFile):
	f = Font(ufo)
	enc = readFile(orderFile)
	print enc.split()
	f.lib['public.glyphOrder'] = enc.split()
	f.save()
def renameGlyphs(ufo):
	proportional = 'guOne.pnum guSix.pnum guTwo.pnum guSeven.pnum guEight.pnum guZero.pnum guNine.pnum guFour.pnum guThree.pnum guFive.pnum'.split()
	tabular = 'guOne guSix guTwo guSeven guEight guZero guNine guFour guThree guFive'.split()
	swapdict = dict(zip(tabular, proportional))
	f = Font(ufo)
	for (left, right), value in f.kerning.items():
		if left in swapdict:
			del f.kerning[left,right]
			left = swapdict[left]
			f.kerning[left,right] = value
		if right in swapdict:
			del f.kerning[left,right]
			right = swapdict[right]
			f.kerning[left,right] = value
		else:
			continue
# 	print left, right			
# 	for left, right in f.kerning.keys():
# 		if left in swapdict:
# 			print left, right, '->',
# 			left = swapdict[left]
# 			print left, right
# 			print
# 		if right in swapdict:
# 			print left, right, '->',
# 			right = swapdict[right]
# 			print left, right
# 			print
	print 'done'
	f.save()

if __name__ == "__main__":
	startTime = time.time()
	# option = sys.argv[1]
	ufo = sys.argv[-1]
 	orderFile = sys.argv[1]
 	madLib(ufo, orderFile)
	
# 	filePath = sys.argv[1]
# 	classes = readKerningClasses(filePath)
# 	pairs = readKerningPairs(filePath)
# 	renameGlyphs(ufo)
	endTime = round(time.time() - startTime, 2)
	print '%s seconds.' % endTime
	# 
# 	replaceKerning(ufo, classes, pairs)
	