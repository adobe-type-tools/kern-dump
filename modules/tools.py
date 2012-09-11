#!/usr/bin/python
import string
import itertools
import re

def readFile(filePath):
	file = open(filePath, 'r')
	fileLinesString = file.read()
	file.close()
	return fileLinesString


class kerningClass(object):
	"Container class for storing kerning classes."
	def __init__(self):
		self.glyphs = []
		self.name = ''
		self.side = ''
		

def sortGlyphs(glyphlist):
	"""\
	This function is sorting the glyphs in a way that glyphs from the exception list or glyphs starting with 'uni' names don't get 
	to be key (first) glyphs. Also, an infinite loop is avoided, in case there are only glyphs matching above mentioned properties.
	"""
	exceptionList = 'dotlessi dotlessj kgreenlandic ae oe AE OE uhorn'.split()

	glyphs = sorted(glyphlist)
	# sorting the strings by length and then alphabetically

	sort_key = lambda s: (len(s), s)
	glyphs.sort(key=sort_key)

	for i in range(len(glyphs)):
		if glyphs[0] in exceptionList or glyphs[0].startswith('uni') or '_' in glyphs[0]:
			glyphs.insert(len(glyphs), glyphs.pop(0))
		else:
			continue

	return glyphs


def nameClass(glyphlist, flag):
	"This function returns a string; which can be used a class name for a list of glyphs, which has ideally been sorted via sortGlyphs."
	glyphs = sortGlyphs(glyphlist)	
	if len(glyphs) == 0:
		print 'class is empty'
		return
	else:
		name = glyphs[0]

	if name in string.ascii_lowercase:
		case = '_LC'
	elif name in string.ascii_uppercase:
		case = '_UC'
	else:
		case = ''

	flag = '_%s' % flag
	
	return '@%s%s%s' % (name, flag, case)


def explode(leftClass, rightClass):
	"Returns a list of tuples, containing all possible combinations of elements in both input lists."
	return list(itertools.product(leftClass, rightClass))


def askForClassName(glyph, side, classes):
	"Given a glyph, a side (LEFT or RIGHT), and the list where classes are stored; this function will return the corresponding class name."
	for singleClass in classes:
		if glyph in singleClass.glyphs and singleClass.side == side:
			return singleClass.name
			break


def askForClassGlyphs(glyph, side, classes):
	"Given a glyph, a side (LEFT or RIGHT), and the list where classes are stored; this function will return the whole kerning class; including the orginal glyph, as a list."
	for singleClass in classes:
		if glyph in singleClass.glyphs and singleClass.side == side:
			return singleClass.glyphs
			break
	

def makeKerningClasses(singlePairsList):
	"""\
	This function analyzes a singlePairsList, and boils them down to a list of kerning classes in the following format:
	
	class:
		kerningClass.name (string) "L_UC_LEFT"
		kerningClass.side (string) "LEFT" or "RIGHT"
		kerningClass.glyphs (list)	
	"""
	
	def makeGlyphValueDict(flag):
		" Creating dictionaries filled with dictionaries, for all the and right and left glyphs that are in a flat kerning pair. "
		" Those are containers used in the next loop. "
		
		glyphsDict = {}
	 	
		for left, right, value in singlePairsList:
			 # the same function can be used for right-left kerning pairs; for the sake of simplicity; the variables are just flipped.
			if flag == 'RIGHT':
				left, right = right, left
			if not left in glyphsDict:
				glyphsDict[left] = {}

			""" 
			Filling dicts created above; creating a list of glyphs that are kerned to their kern partner _value_.
			This creates dictionaries like this:
	
			q:	{
				-61: ['quoteright.latn', 'quoteright.latn', 'quotedblright.latn'], 
				-57: ['quoteleft.latn', 'quoteleft.latn', 'quotedblleft.latn'],
				}

			Same is happening for the right side; where the kerning needs to be imagined in reverse (right glyph to left glyph: value).
			"""

		for left, right, value in singlePairsList:
			if flag == 'RIGHT':
				left, right = right, left
				
			if not value in glyphsDict[left]:
				glyphsDict[left][value] = []
				glyphsDict[left][value].append(right)
			else:
				if not left in glyphsDict[left][value]:
					glyphsDict[left][value].append(right)

		return glyphsDict
		
		
	leftGlyphsDict = makeGlyphValueDict('LEFT')
	rightGlyphsDict = makeGlyphValueDict('RIGHT')

	def reduceGlyphDict(glyphsDict):
		" Sorting aforementioned lists of glyphs; adding them to a list that contains all the right/left classes found via above method. "
		" This will not be the final list of classes, just all possible ones. "
		
		allClasses = []
		potentialClasses = []

		for glyph in glyphsDict:
			for kernValue in glyphsDict[glyph]:
				kernClass = sortGlyphs(glyphsDict[glyph][kernValue])
				allClasses.append(kernClass)

		" Counting occurrence and length of those classes; throwing out the ones that have length == 1 or occur only once. "

		for c in allClasses:
			occurrence = allClasses.count(c)
			
			# the occurrence value could be higher; probably this would increase accuracy in the end.
			if occurrence > 3 and len(c) > 1:
			 	if (occurrence, c) not in potentialClasses:
			 		potentialClasses.append((occurrence, c))


		" Sorting the potential classes by occurrence; so we can parse them by importance. "
		potentialClasses.sort()
		potentialClasses.reverse()
		return potentialClasses

	" This is NOT a mistake! To find the potential right classes, we need to parse the leftGlyphsDict; and vice versa."
	potentialRightClasses = reduceGlyphDict(leftGlyphsDict)
	potentialLeftClasses = reduceGlyphDict(rightGlyphsDict)

	def makeFinalClasses(potentialClasses):
		""" 
		The potential classes are sorted by occurrence.
		In this function, we parse the list of classes over and over again, removing the higher-ranked class
		from all the remaining classes below, to come up with classes that have the highest probability. 
		"""
		finalClasses = []
		for i in potentialClasses:
			classIndex = potentialClasses.index(i)
			glyphs = i[1]

			for k in potentialClasses[classIndex:]:
				targetIndex = potentialClasses.index(k)
				otherglyphs = k[1]
				k = (k[0], list(set(otherglyphs) - set(glyphs)))
				potentialClasses[targetIndex] = k

			if len( glyphs ) > 0:
				finalClasses.append(sortGlyphs(glyphs))
		return sorted(finalClasses)
	
	finalRightClasses = makeFinalClasses(potentialRightClasses)
	finalLeftClasses = makeFinalClasses(potentialLeftClasses)
	
	classes = [] # the final container in which kerning classes are stored as python classes

	def storeClasses(inputfile, flag):
		for i in inputfile:
			c = kerningClass()
			c.glyphs = i
			c.side = flag
			c.name = nameClass(i, flag)
			classes.append(c)
	
	storeClasses(finalRightClasses, 'RIGHT')
	storeClasses(finalLeftClasses, 'LEFT')
	return classes


def readKerningClasses(path):

	kernClassesString = readFile(path)
	allClassesList = re.findall(r"@(\S+)\s*=\s*\[([ A-Za-z0-9_.]+)\]\s*;", kernClassesString)

	classes = []
	for name, glyphs in allClassesList:
		c = kerningClass()
		c.name = '@%s' % name
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

			d = kerningClass()
			d.name = c.name
			d.glyphs = c.glyphs
			d.side = 'RIGHT'
			classes.append(d)
		
	return classes
	
def readKerningPairs(path):

	kernPairsString = readFile(path)
	allPairsList = re.findall(r"pos\s*([@A-Za-z0-9_.]+?)\s*([@A-Za-z0-9_.]+?)\s*(-?\d+?);", kernPairsString)

	# classes = []
	# for name, glyphs in allClassesList:
	# 	c = kerningClass()
	# 	c.name = '@%s' % name
	# 	c.glyphs = glyphs.split()
	# 
	# 	if name.split('_')[-1] == 'LEFT':
	# 		c.side = 'LEFT'
	# 		classes.append(c)
	# 	elif name.split('_')[-1] == 'RIGHT':
	# 		c.side = 'RIGHT'
	# 		classes.append(c)
	# 	else:
	# 		c.side = 'LEFT'
	# 		classes.append(c)
	# 
	# 		d = kerningClass()
	# 		d.name = c.name
	# 		d.glyphs = c.glyphs
	# 		d.side = 'RIGHT'
	# 		classes.append(d)
		
	return allPairsList
	
