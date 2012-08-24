import os, sys
import inspect
import string
from fontTools import ttLib

kKernFeatureTag = 'kern'
li = []
class myLeftClass:
	def __init__(self):
		self.glyphs = []
		self.class1Record = 0

class myRightClass:
	def __init__(self):
		self.glyphs = []
		self.class2Record = 0

def sortGlyphs(glyphlist):
	# This function is sorting the glyphs in a way that glyphs in the exception list; or glyphs with 'uni' names don't get to be key glyphs.
	# Also, an infinite loop is avoided, in case there are only glyphs matching above mentioned properties.
	exceptionList = 'dotlessi dotlessj kgreenlandic ae oe AE OE uhorn'.split()

	glyphs = sorted(glyphlist)
	for i in range(len(glyphs)):
		if glyphs[0] in exceptionList or glyphs[0].startswith('uni'):
			glyphs.insert(len(glyphs), glyphs.pop(0))
		else:
			pass

	return glyphs

def nameClass(glyphlist, flag):
	glyphs = sortGlyphs(glyphlist)	
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
	glyphPairsDict = {}
### ScriptList ###
# 	scriptList = gposTable.ScriptList

### FeatureList ###
	featureList = gposTable.FeatureList
# 	featureCount = featureList.FeatureCount # integer
	featureRecord = featureList.FeatureRecord
	
	uniqueKernLookupListIndexesList = collectUniqueKernLookupListIndexes(featureRecord)
	
	# Make sure a 'kern' feature was found
	if not len(uniqueKernLookupListIndexesList):
		print "The font has no 'kern' feature"
		return

### LookupList ###
	lookupList = gposTable.LookupList
	
	for kernLookupIndex in uniqueKernLookupListIndexesList:
		lookup = lookupList.Lookup[kernLookupIndex]
		
		# Confirm this is a GPOS LookupType 2 lookup
		if lookup.LookupType != 2:
			print "This is not a pair adjustment positioning lookup (GPOS LookupType 2)"
			return
		
		# Step through each subtable
		for subtableItem in lookup.SubTable:
			pairPos = subtableItem
			
# 			if pairPos.Format not in [1]:
# 				print "WARNING: PairPos format %d is not yet supported" % pairPos.Format
			
			if pairPos.Coverage.Format not in [1,2]:
				print "WARNING: Coverage format %d is not yet supported" % pairPos.Coverage.Format
			
			if pairPos.ValueFormat1 not in [4]:
				print "WARNING: ValueFormat1 format %d is not yet supported" % pairPos.ValueFormat1
			
			if pairPos.ValueFormat2 not in [0]:
				print "WARNING: ValueFormat2 format %d is not yet supported" % pairPos.ValueFormat2
			
			# each glyph in this list will have a corresponding PairSet which will
			# contain all the second glyphs and the kerning value in the form of PairValueRecord(s)
			firstGlyphsList = pairPos.Coverage.glyphs
#			print firstGlyphsList
			
			if pairPos.Format == 1: # glyph pair adjustment; format 2 is class pair adjustment
			
				# This iteration is done by index so that we have a way to reference the firstGlyphsList list
				for pairSetIndex in range(len(pairPos.PairSet)):
#					print 'xxx', len(pairPos.PairSet), 'xxx'
					for pairValueRecordItem in pairPos.PairSet[pairSetIndex].PairValueRecord:
#						print dir(pairValueRecordItem)
						secondGlyph = pairValueRecordItem.SecondGlyph
						kernValue = pairValueRecordItem.Value1.XAdvance
						
						singlePairsList.append((firstGlyphsList[pairSetIndex], secondGlyph, kernValue))
#						glyphPairsDict[(firstGlyphsList[pairSetIndex], secondGlyph)] = kernValue


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
 					

					
# 				for i in rightClasses:
# 					print rightClasses[i].class2Record, sorted(rightClasses[i].glyphs)

				for record in leftClasses:
					for j in rightClasses:
#					record = i #
						if pairPos.Class1Record[record].Class2Record[j]:
							kernValue = pairPos.Class1Record[record].Class2Record[j].Value1.XAdvance
							if kernValue != 0:

# 								leftGlyphs = sorted(leftClasses[record].glyphs)
# 								if leftGlyphs[0] in exceptionList or leftGlyphs[0].startswith('uni'):
# 									leftGlyphs.insert(len(leftGlyphs)+1, leftGlyphs.pop(0))
								leftGlyphs = sortGlyphs(leftClasses[record].glyphs)

# 								rightGlyphs = sorted(rightClasses[j].glyphs)
# 								if rightGlyphs[0] in exceptionList or rightGlyphs[0].startswith('uni'):
# 									rightGlyphs.insert(len(rightGlyphs), rightGlyphs.pop(0))
								rightGlyphs = sortGlyphs(rightClasses[j].glyphs)

								leftClass = nameClass(leftGlyphs, '_LEFT')
								rightClass = nameClass(rightGlyphs, '_RIGHT')
								
# 								keyLeft = leftGlyphs[0]
# 								keyRight = rightGlyphs[0]


# 								for l in leftClasses[record].glyphs:
# 									for r in rightClasses[j].glyphs:
	#									print l, r, kernValue
#										glyphPairsList.append((l, r, kernValue))
# 										if (l, r) in glyphPairsDict:
# 											continue

								classPairsList.append((leftClass, rightClass, kernValue))
							
						else:
							print 'ERROR'

	
	
	for i in leftClasses:
 		glyphs = sorted(leftClasses[i].glyphs)
		className = nameClass(glyphs, '_LEFT')
 		
 		print '%s = [ %s ];' % (className, ' '.join(glyphs))

	for i in rightClasses:
		glyphs = sorted(rightClasses[i].glyphs)
		className = nameClass(glyphs, '_RIGHT')
 		
 		print '%s = [ %s ];' % (className, ' '.join(glyphs))
	
	print
	print 
	
	for left, right, value in singlePairsList:
		print 'pos %s %s %s;' % (left, right, value)

	print
	print 

	for left, right, value in classPairsList:
		print 'pos %s %s %s;' % (left, right, value)


	
# 	for pair, value in glyphPairsDict.items():
# 	 	li.append('/%s /%s %s' % ( pair[0], pair[1], value ))
# 			
# 	li.sort()
# 	output = '\n'.join(li)
# 	scrap = os.popen('pbcopy', 'w')
# 	scrap.write(output)
# 	scrap.close()

#	print 'done'


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