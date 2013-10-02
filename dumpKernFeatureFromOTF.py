import os, sys
import inspect
import string
from fontTools import ttLib

import getKerningPairs
reload(getKerningPairs)

__doc__ ='''\

	This script extracts a viable kern feature file from a compiled OTF.

	usage: python getKerning font.otf > outputfile

	'''

kKernFeatureTag = 'kern'


def sortGlyphs(glyphlist):
	# Sort the glyphs in a way that glyphs from the exception list or glyphs starting with 'uni' names do not get to be key (first) glyphs. 
	# An infinite loop is avoided, in case there are only glyphs matching above mentioned properties.
	exceptionList = 'dotlessi dotlessj kgreenlandic ae oe AE OE uhorn'.split()

	glyphs = sorted(glyphlist)
	for i in range(len(glyphs)):
		if glyphs[0] in exceptionList or glyphs[0].startswith('uni'):
			glyphs.insert(len(glyphs), glyphs.pop(0))
		else:
			continue

	return glyphs


def nameClass(glyphlist, flag):
	glyphs = sortGlyphs(glyphlist)	
	if len(glyphs) == 0:
		name = 'error!!!'
	else:
		name = glyphs[0]

	if name in string.ascii_lowercase:
		case = '_LC'
	elif name in string.ascii_uppercase:
		case = '_UC'
	else:
		case = ''

	flag = flag
	
	return '@%s%s%s' % (name, flag, case)


def makeFeature(fontPath):
	f = getKerningPairs.Analyze(fontPath)
	allClasses = {}

	for kerningClass in f.allLeftClasses:
		glyphs = sortGlyphs(f.allLeftClasses[kerningClass])
		className = nameClass(glyphs, '_LEFT')
		allClasses.setdefault(className, glyphs)

	for kerningClass in f.allRightClasses:
		glyphs = sortGlyphs(f.allRightClasses[kerningClass])
		className = nameClass(glyphs, '_RIGHT')
		allClasses.setdefault(className, glyphs)

	singlePairsList = sorted(f.singlePairs.items())

	classPairsList = []
	for (leftClass, rightClass), value in sorted(f.classPairs.items()):
		leftGlyphs = sortGlyphs(f.allLeftClasses[leftClass])
		leftClassName = nameClass(leftGlyphs, '_LEFT')

		rightGlyphs = sortGlyphs(f.allRightClasses[rightClass])
		rightClassName = nameClass(rightGlyphs, '_RIGHT')

		classPairsList.append(((leftClassName, rightClassName), value))


	leftGlyphsDict = {}
	rightGlyphsDict = {}

	compressedLeft = []
	compressedBoth = []

	class_glyph = []
	glyph_class = []
	glyph_glyph = []
	exploded_class_class = []	# this is not really class to class; as it will be exploded into single pairs.


	# # Here, we compress the single pairs to a more space-saving notation.
	# # First, dictionaries for each left glyph are created. 
	# # If the kerning value to any right glyph happens to be equal, those right glyphs are merged into a class.

	for (left, right), value in singlePairsList:
		leftGlyph = left 
		# leftGlyphsDict.setdefault(leftGlyph, {}).setdefault(value, []).append(right) # shorter
		leftGlyphsDict.setdefault(leftGlyph, {})
		kernValueDict = leftGlyphsDict[leftGlyph]
		kernValueDict.setdefault(value, []).append(right)

	for left in leftGlyphsDict:
		for value in leftGlyphsDict[left]:
			right = leftGlyphsDict[left][value]
			right = sortGlyphs(right)
			compressedLeft.append((left, right, value))
				
	# same happens for the right side; including classes that have been compressed before.

	for left, right, value in compressedLeft:
		rightGlyph = ' '.join( right )
		rightGlyphsDict.setdefault(rightGlyph, {})
		kernValueDict = rightGlyphsDict[rightGlyph]
		kernValueDict.setdefault(value, []).append(left)

	for right in rightGlyphsDict:
		for value in rightGlyphsDict[right]:
			left = rightGlyphsDict[right][value]
			left = sortGlyphs(left)
			compressedBoth.append((left, right.split(), value))


	# Splitting the compressed single-pair kerning into four different lists; organized by type:
	for left, right, value in compressedBoth:
		if len(left) != 1 and len(right) != 1:
			exploded_class_class.append('enum pos [ %s ] [ %s ] %s;' % (' '.join(left), ' '.join(right), value))
		elif len(left) != 1 and len(right) == 1:
			class_glyph.append('enum pos [ %s ] %s %s;'		% (' '.join(left), ' '.join(right), value))
		elif len(left) == 1 and len(right) != 1:
			glyph_class.append('enum pos %s [ %s ] %s;'	% (' '.join(left), ' '.join(right), value))
		elif len(left) == 1 and len(right) == 1:
			glyph_glyph.append('pos %s %s %s;'				% (' '.join(left), ' '.join(right), value))
		else:
			print 'ERROR with (%s)' % (' '.join(left, right, value))

	# Making sure all the pairs made it through the process:
	if len(compressedBoth) != len(class_glyph) + len(glyph_class) + len(glyph_glyph) + len(exploded_class_class):
		print 'ERROR - we lost some kerning pairs.'



	print '# kern feature dumped from %s' % os.path.basename(fontPath)
	print '#', '-'*100
	print
	for className in sorted(allClasses):
		glyphs = allClasses[className]
			
		print '%s = [ %s ];' % (className, ' '.join(glyphs))
	
	
	
	print
	print
	print '# glyph to glyph'		
	print '#', '-'*100
	for i in glyph_glyph:
		print i
	
	print
	print '# glyph to class'		
	print '#', '-'*100
	for i in glyph_class:
		print i
	print
	print '# class to glyph'		
	print '#', '-'*100
	for i in class_glyph:
		print i
	print	
	print '# exploding class to exploding class'	
	print '#', '-'*100
	for i in exploded_class_class:
		print i


	# # This was the old output for there was only a single pairs list (without compression).

	# # print
	# # print '# glyph to glyph'		
	# # print '#', '-'*100
	# # for left, right, value in singlePairsList:
	# #	print 'pos %s %s %s;' % (left, right, value)
	
	print	
	print '# class to class'		
	print '#', '-'*100
	for (left, right), value in classPairsList:
		print 'pos %s %s %s;' % (left, right, value)





if __name__ == "__main__":
	if len(sys.argv) == 2:
		if os.path.exists(sys.argv[1]):
			fontPath = sys.argv[1]
   		makeFeature(fontPath)

	else:
		print "No valid font provided."