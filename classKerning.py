import os, sys
# import itertools
import time
from modules.fromGPOS import *
# from fontTools import ttLib
import operator

__doc__ ='''\

	This script is capable of extracting a viable features.kern file from a compiled font.
	To be expanded with multiple options; e.g. AFM-export; and export of all possible (exploded) pairs.

	usage: python getKerning font.otf > outputfile

	'''
	
def outputFile(path, suffix):
 	return '%s.%s' % (os.path.splitext(fontPath)[0], suffix)


def write2file(path, list):
	o = open(path, 'w')
	o.write('\n'.join(list))
	o.close()


def output(classes, singlePairsList, classKerning):
	output = [ ]

	leftClasses = [i for i in classes if i.side == 'LEFT']
	rightClasses = [i for i in classes if i.side == 'RIGHT']

	def sortClass(classList):
		return sorted(classList, key=operator.attrgetter('name'))

	for i in sortClass(leftClasses):
		output.append( '%s = [ %s ];' % (i.name, ' '.join(i.glyphs) ))
	output.append('')

	for i in sortClass(rightClasses):
		string = '%s = [ %s ];' % (i.name, ' '.join(i.glyphs) )
		if not string in output: # for both-sided classes that might already have been assigned on the left side.
			output.append(string)
	output.append('')

	for left, right, value in singlePairsList:
		output.append( 'pos %s %s %s;' % (left, right, value) )
	output.append('')

	for left, right, value in classKerning:
		output.append( 'pos %s %s %s;' % (left, right, value) )
	output.append('')
	return output


def makeSafeKernFeature(fontPath, singlePairsList, classes):

	leftClassGlyphs = [i.glyphs for i in classes if i.side == 'LEFT']
	rightClassGlyphs = [i.glyphs for i in classes if i.side == 'RIGHT']
	explodedClasses = []

	for leftClass, rightClass in explode(leftClassGlyphs, rightClassGlyphs):
		explodedClasses.extend( explode (leftClass, rightClass))
	
	singlePairsDict = {}
	# a dictionary that organizes the single pairs by kern value.
	for left, right, value in singlePairsList:
		if not value in singlePairsDict:
			singlePairsDict[value] = [(left, right)]
		else:
			singlePairsDict[value].append((left,right))
	
	
	classKerning = []
	for left, right, value in singlePairsList[::-1]:
		# First step: checking if the pair is in possible class kerning pairs with classes as we have them (explodedClasses).
	
		if (left, right) in explodedClasses:
			# get the class names for both sides
			leftClass = askForClassName(left, 'LEFT', classes)
			rightClass = askForClassName(right, 'RIGHT', classes)
			classKernPair = leftClass, rightClass, value
	
			if classKernPair in classKerning:
				# remove the pair if it exists
				singlePairsList.remove((left, right, value))
				continue
			else:
				combinations = explode(askForClassGlyphs(left, 'LEFT', classes), askForClassGlyphs(right, 'RIGHT', classes))
				# if the pair does not exist, we look at the classes for left and right glyphs, and all possible 
				# combinations between the two. (exploding both sides against each other)
			
				if set(combinations).issubset(set(singlePairsDict[value])):
					# If all those combinations are a subset of combinations as covered in singlePairsDict[value], 
					# it is safe to assume this pair can be replaced by classkerning.
			
					classKerning.append(classKernPair)
					singlePairsList.remove((left, right, value))
				
		
	data = output(classes, singlePairsList, classKerning)
	outputFileName = outputFile(fontPath, 'kern')
	write2file(outputFileName, data)
	
	print 'done'



def makeExperimentalKernFeature(fontPath, singlePairsList, classes):
	'This method is capable of _adding_ kerning pairs to the original font, depening if they '
	
	# Removing glyphs that might be in the kerning class file imported, but are not in the target font.
 	availableGlyphs = getGlyphNames(fontPath)
	for kerningClass in classes:
		for glyph in kerningClass.glyphs[::-1]:
			if not glyph in availableGlyphs:
				kerningClass.glyphs.remove(glyph)

	for kerningClass in classes[::-1]:
		if len(kerningClass.glyphs) == 0:
			classes.remove(kerningClass)
			
	leftClassGlyphs = [i.glyphs for i in classes if i.side == 'LEFT']
	rightClassGlyphs = [i.glyphs for i in classes if i.side == 'RIGHT']
	explodedClasses = []


	
	for leftClass, rightClass in explode(leftClassGlyphs, rightClassGlyphs):
		explodedClasses.extend( explode (leftClass, rightClass))
	
	
	singlePairsDict = {}
	# a dictionary that organizes the single pairs by kern value.
	for left, right, value in singlePairsList:
		if not value in singlePairsDict:
			singlePairsDict[value] = [(left, right)]
		else:
			singlePairsDict[value].append((left,right))
	
	
	classKerning = []
	exceptions = []
	classPairs = {}
	
	for left, right, value in singlePairsList: 
	
		# First step: checking if the pair is in possible class kerning pairs with classes as we have them (explodedClasses).
		if (left, right) in explodedClasses:
			# get the class names for both sides:
			leftClass = askForClassName(left, 'LEFT', classes)
			rightClass = askForClassName(right, 'RIGHT', classes)
			classPair = leftClass, rightClass
	
			if not classPair in classPairs:
				classPairs[classPair] = {}
				classPairs[classPair][value] = 1
			else:
				if value in classPairs[classPair]:
					classPairs[classPair][value] += 1
				else: 
					classPairs[classPair][value] = 1
	
	
	for p in classPairs:
		l = classPairs[p].items()
		if len( l ) > 1:
			# If a pair of classes is found kerned with different values, the value with maximum occurrence is being picked.
			maxOccurring = max(l, key = lambda x: x[-1])
			bestValue = maxOccurring[0]
		else:
			# only one value is present
			bestValue = classPairs[p].keys()[0]
	
		classPairs[p] = bestValue
		# A dictionary of class kerning pairs, and the value they liked to be kerned by.
	
	
	for left, right, value in singlePairsList[::-1]: 
	
		if (left, right) in explodedClasses:
			leftClass = askForClassName(left, 'LEFT', classes)
			rightClass = askForClassName(right, 'RIGHT', classes)
			classPair = leftClass, rightClass
			classKernPair = leftClass, rightClass, value
			
			if classPairs[classPair] == value:
				if classKernPair not in classKerning:
					classKerning.append(classKernPair)
				singlePairsList.remove((left, right, value))
			elif classPairs[classPair] != value:
				exceptions.append((left, right, value))
				singlePairsList.remove((left, right, value))
	

	

	# allRightClassGlyphs = [i for sublist in rightClassGlyphs for i in sublist] # works as well, faster; but not understandable.
	allRightClassGlyphs = sum(rightClassGlyphs, [])
	allLeftClassGlyphs = sum(leftClassGlyphs, [])
	remainingLeft = []
	remainingRight = []
	
	for left, right, value in singlePairsList:
		if not left in allLeftClassGlyphs and not left in remainingLeft:
			remainingLeft.append(left)
	
	for left, right, value in singlePairsList:
		if not right in allRightClassGlyphs and not right in remainingRight:
			remainingRight.append(right)
	
	decoration = ' >^.^< ' * 10
	print decoration
	print "Unclassy glyphs remaining on left side:\n%s" % (', '.join(sorted(remainingLeft)))
	print
	print decoration
	print "Unclassy glyphs remaining on right side:\n%s" % (', '.join(sorted(remainingRight)))
	print decoration
	print	
	
	# throwing the identified exception back into the single pairs list.
	singlePairsList.extend(exceptions)
	
	data = output(classes, singlePairsList, classKerning)
	outputFileName = outputFile(fontPath, 'kern')
	write2file(outputFileName, data)
	
	print "Let me show you how it's done. It took",


def test(fontPath, singlePairsList):
	print singlePairsList


if __name__ == "__main__":
	startTime = time.time()
	
	option = sys.argv[1]

	if option == '-font':
		if os.path.exists(sys.argv[-1]):
			fontPath = sys.argv[-1]
			singlePairsList = getSinglePairs(fontPath)
			classes = makeKerningClasses(singlePairsList)
	   		makeSafeKernFeature(fontPath, singlePairsList, classes)
		else:
			print "No valid font provided."

	elif option == '-file':
		fontPath = sys.argv[-1]
		filePath = sys.argv[2]
		singlePairsList = getSinglePairs(fontPath)
		classes = readKerningClasses(filePath)
		makeExperimentalKernFeature(fontPath, singlePairsList, classes)
		
	elif option == '-test':
		fontPath = sys.argv[-1]
		singlePairsList = getSinglePairs(fontPath)
		test(fontPath, singlePairsList)

	
	else:
		print 'no option used'
	
	
	# if len(sys.argv) == 2:

	endTime = round(time.time() - startTime, 2)
	# print 'It took %s seconds to run this script.' % endTime
	print '%s seconds.' % endTime
	