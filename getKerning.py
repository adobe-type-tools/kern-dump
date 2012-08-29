import os, sys
import inspect
import string
from fontTools import ttLib


__doc__ ='''\

	This script is capable of extracting a viable features.kern file from a compiled font.
	To be expanded with multiple options; e.g. AFM-export; and export of all possible (exploded) pairs.

	usage: python getKerning font.otf > outputfile

	'''

kKernFeatureTag = 'kern'

class myLeftClass:
	def __init__(self):
		self.glyphs = []
		self.class1Record = 0

class myRightClass:
	def __init__(self):
		self.glyphs = []
		self.class2Record = 0


def sortGlyphs(glyphlist):
	# This function is sorting the glyphs in a way that glyphs from the exception list or glyphs starting with 'uni' names don't get 
	# to be key (first) glyphs. Also, an infinite loop is avoided, in case there are only glyphs matching above mentioned properties.
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


def collectUniqueKernLookupListIndexes(featureRecord):
	uniqueKernLookupListIndexesList = []
	for featRecItem in featureRecord:
# 		print featRecItem.FeatureTag  # GPOS feature tags (e.g. kern, mark, mkmk, size) of each ScriptRecord
		if featRecItem.FeatureTag == kKernFeatureTag:
			feature = featRecItem.Feature
			
			for featLkpItem in feature.LookupListIndex:
				if featLkpItem not in uniqueKernLookupListIndexesList:
					uniqueKernLookupListIndexesList.append(featLkpItem)
	
	return uniqueKernLookupListIndexesList


def main(fontPath):
	font = ttLib.TTFont(fontPath)
	
	gposTable = font['GPOS'].table
	
	glyphPairsList = []
	singlePairsList = []
	classPairsList	= []
	# leftClasses = {}
	# rightClasses = {}
	allClasses = {}

### ScriptList ###
# 	scriptList = gposTable.ScriptList

### FeatureList ###
	featureList = gposTable.FeatureList
	# featureCount = featureList.FeatureCount # integer
	featureRecord = featureList.FeatureRecord
	
	uniqueKernLookupListIndexesList = collectUniqueKernLookupListIndexes(featureRecord)
	
	# Make sure a 'kern' feature was found
	if not len(uniqueKernLookupListIndexesList):
		print "The font has no 'kern' feature"
		return

### LookupList ###
	lookupList = gposTable.LookupList
	for kernLookupIndex in sorted(uniqueKernLookupListIndexesList):
		lookup = lookupList.Lookup[kernLookupIndex]
		# Confirm this is a GPOS LookupType 2; or using an extension table (GPOS LookupType 9):
		if lookup.LookupType not in [2, 9]:
			print "This is not a pair adjustment positioning lookup (GPOS LookupType 2); and not using an extension table (GPOS LookupType 9).\nInstead, it is GPOS LookupType %s!" % lookup.LookupType
			continue
		
		# Step through each subtable
		for subtableItem in lookup.SubTable:
			if subtableItem.LookupType == 2: # normal case, not using extension table
				pairPos = subtableItem
			elif subtableItem.LookupType == 9: # If extension table is used
				if subtableItem.ExtensionLookupType == 8:
					continue
					# ExtensionPos == subtable!
					
					# those work!
					# print subtableItem.ExtSubTable
					# print subtableItem.ExtSubTable.convertersByName[1]['Coverage'].name
					# print dir(subtableItem.ExtSubTable.getConverterByName)
					# print subtableItem.ExtSubTable.getConverterByName
					# membersList = inspect.getmembers(subtableItem.ExtSubTable.getConverterByName)
					# for x in membersList:
					# 	print x
					# print
				elif subtableItem.ExtensionLookupType == 2:
					pairPos = subtableItem.ExtSubTable
					

			# if pairPos.Format not in [1]:
			# 	print "WARNING: PairPos format %d is not yet supported" % pairPos.Format
			
			if pairPos.Coverage.Format not in [1,2]:
				print "WARNING: Coverage format %d is not yet supported" % pairPos.Coverage.Format
			
			if pairPos.ValueFormat1 not in [4]:
				print "WARNING: ValueFormat1 format %d is not yet supported" % pairPos.ValueFormat1
			
			if pairPos.ValueFormat2 not in [0]:
				print "WARNING: ValueFormat2 format %d is not yet supported" % pairPos.ValueFormat2
			
			# each glyph in this list will have a corresponding PairSet which will
			# contain all the second glyphs and the kerning value in the form of PairValueRecord(s)
			firstGlyphsList = pairPos.Coverage.glyphs

			if pairPos.Format == 1: # glyph pair adjustment; format 2 is class pair adjustment
			
				# This iteration is done by index so that we have a way to reference the firstGlyphsList list
				for pairSetIndex in range(len(pairPos.PairSet)):
					for pairValueRecordItem in pairPos.PairSet[pairSetIndex].PairValueRecord:
						firstGlyph = firstGlyphsList[pairSetIndex]
						secondGlyph = pairValueRecordItem.SecondGlyph
						kernValue = pairValueRecordItem.Value1.XAdvance
						
						# singlePairsList.append(('%s %s' %( kernLookupIndex, firstGlyph), secondGlyph, kernValue))
						singlePairsList.append((firstGlyph, secondGlyph, kernValue))


			############################################
			############################################
			############################################

			elif pairPos.Format == 2: # class adjustment
				firstGlyphs = {}
				secondGlyphs = {}

				leftClasses = {}
				rightClasses = {}
				
				# Find left class with the Class1Record index="0".
				# This class is weirdly mixed into the "Coverage" (e.g. all left glyphs) 
				# and has no class="X" property, that is why we have to find them that way. 
				lg0 = myLeftClass()
				for leftGlyph in firstGlyphsList:
					if not leftGlyph in pairPos.ClassDef1.classDefs:
						lg0.glyphs.append(leftGlyph)
				# This mixing into the Coverage is true for makeOTF-built fonts. 
				# There are fonts which have all the glyphs properly assgned; therefore this if-statement:
				if not len(lg0.glyphs) == 0:
					leftClasses[lg0.class1Record] = lg0		

				# Find all the remaining left classes:
 				for leftGlyph in pairPos.ClassDef1.classDefs:
 					class1Record = pairPos.ClassDef1.classDefs[leftGlyph]
 					if class1Record in leftClasses:
	 					leftClasses[class1Record].glyphs.append(leftGlyph)
	 				else:
	 					lg = myLeftClass()
	 					lg.class1Record = class1Record
	 					leftClasses[class1Record] = lg
	 					leftClasses[class1Record].glyphs.append(leftGlyph)

				# Same for the right classes:
				for rightGlyph in pairPos.ClassDef2.classDefs:					
 					class2Record = pairPos.ClassDef2.classDefs[rightGlyph]
 					if class2Record in rightClasses:
	 					rightClasses[class2Record].glyphs.append(rightGlyph)
	 				else:
	 					rg = myRightClass()
	 					rg.class2Record = class2Record
	 					rightClasses[class2Record] = rg
	 					rightClasses[class2Record].glyphs.append(rightGlyph)
 				
				for record_l in leftClasses:
					for record_r in rightClasses:
						if pairPos.Class1Record[record_l].Class2Record[record_r]:
							kernValue = pairPos.Class1Record[record_l].Class2Record[record_r].Value1.XAdvance
							if kernValue != 0:

								leftGlyphs = sortGlyphs(leftClasses[record_l].glyphs)

								rightGlyphs = sortGlyphs(rightClasses[record_r].glyphs)

								leftClass = nameClass(leftGlyphs, '_LEFT')
								rightClass = nameClass(rightGlyphs, '_RIGHT')
								
								if (leftClass, rightClass, kernValue) in classPairsList:
									pass
								else:
									# classPairsList.append(('%s %s' % (kernLookupIndex, leftClass), rightClass, kernValue))
									classPairsList.append((leftClass, rightClass, kernValue))
							
						else:
							print 'ERROR'
			
				for i in leftClasses:
			 		glyphs = sortGlyphs(leftClasses[i].glyphs)
					className = nameClass(glyphs, '_LEFT')
					if not className in allClasses:
						allClasses[className] = glyphs
				
				for i in rightClasses:
					glyphs = sortGlyphs(rightClasses[i].glyphs)
					className = nameClass(glyphs, '_RIGHT')
					if not className in allClasses:
						allClasses[className] = glyphs
				

	
	leftGlyphsDict = {}
	rightGlyphsDict = {}

	compressedLeft = []
	compressedBoth = []

	class_glyph = []
	glyph_class = []
	glyph_glyph = []

	# this is not really class to class; as it will be exploded into single pairs.
	class_class = []


	# Here, we compress the single pairs to a more space-saving notation.
	# First, dictionaries for each left glyph are created. 
	# If the kerning value to any right glyph happens to be equal, those right glyphs are merged into a class.
 	for left, right, value in singlePairsList:
		leftGlyph = left 
		if not leftGlyph in leftGlyphsDict:
			leftGlyphsDict[leftGlyph] = {}
			di = leftGlyphsDict[leftGlyph]
		else:
			di = leftGlyphsDict[leftGlyph]

		if not value in di:
			di[value] = [right]
		else:
			di[value].append(right)

	for left in leftGlyphsDict:
		for value in leftGlyphsDict[left]:
			right = leftGlyphsDict[left][value]
			right = sortGlyphs(right)
			compressedLeft.append((left, right, value))
				
	# same happens for the right side; including classes that have been compressed before.
 	for left, right, value in compressedLeft:
		rightGlyph = ' '.join( right )
		if not rightGlyph in rightGlyphsDict:
			rightGlyphsDict[rightGlyph] = {}
			di = rightGlyphsDict[rightGlyph]
		else:
			di = rightGlyphsDict[rightGlyph]
		if not value in di:
			di[value] = [left]
		else:
			di[value].append(left)

	for right in rightGlyphsDict:
		for value in rightGlyphsDict[right]:
 			left = rightGlyphsDict[right][value]
			left = sortGlyphs(left)
			compressedBoth.append((left, right.split(), value))

	
	# Splitting the compressed single-pair kerning into four different lists; organized by type:
 	for left, right, value in compressedBoth:
 		if len(left) != 1 and len(right) != 1:
			class_class.append('enum pos [ %s ] [ %s ] %s;' % (' '.join(left), ' '.join(right), value))
		elif len(left) != 1 and len(right) == 1:
			class_glyph.append('enum pos [ %s ] %s %s;' % (' '.join(left), ' '.join(right), value))
		elif len(left) == 1 and len(right) != 1:
			glyph_class.append('enum pos %s [ %s ] %s;' % (' '.join(left), ' '.join(right), value))
		elif len(left) == 1 and len(right) == 1:
			glyph_glyph.append('pos %s %s %s;' % (' '.join(left), ' '.join(right), value))
		else:
			print 'ERROR with (%s)' % (' '.join(left, right, value))

	# Making sure all the pairs made it through the process:
	if len(compressedBoth) != len(class_glyph) + len(glyph_class) + len(glyph_glyph) + len(class_class):
		print 'ERROR - we lost some kerning pairs.'


	# OUTPUT STARTS HERE #####################
	##########################################
	# (this needs to be heavily reorganized) #
	##########################################

	print '# kern feature dumped from %s' % os.path.basename(fontPath)
	print '#', '-'*100
	print
	for i in allClasses:
 		glyphs = allClasses[i]
		className = i
	 		
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
	for i in class_class:
		print i


	# This was the old output for when we only had one single pairs list (without compression).

	# print
	# print '# glyph to glyph'		
	# print '#', '-'*100
	# for left, right, value in singlePairsList:
	# 	print 'pos %s %s %s;' % (left, right, value)
	
	print	
	print '# class to class'		
	print '#', '-'*100
	for left, right, value in classPairsList:
		print 'pos %s %s %s;' % (left, right, value)



# 	membersList = inspect.getmembers(pairPos.ClassDef1.classDefs)
# 	for x in membersList:
# 		print x
# 	print
# 	print
	


if __name__ == "__main__":
	if len(sys.argv) == 2:
		if os.path.exists(sys.argv[1]):
			fontPath = sys.argv[1]
    		main(fontPath)
	else:
		print "No valid font provided."