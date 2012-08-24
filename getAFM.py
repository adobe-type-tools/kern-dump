import os, sys
import inspect
from fontTools import ttLib

kKernFeatureTag = 'kern'
li = []

class myLeftGlyph:
	def __init__(self, glyphName, kernPartner):
		self.glyphName = glyphName
		self.kernPartner = kernPartner


class myRightGlyph:
	def __init__(self, glyphName, kernRecord, kernValue):
		self.glyphName = glyphName
		self.kernRecord = kernRecord
		self.kernValue = kernValue


class myLeftClass:
	def __init__(self):
		self.glyphs = []
		self.class1Record = 0

class myRightClass:
	def __init__(self):
		self.glyphs = []
		self.class2Record = 0


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
		
		# Confirm this is a GPOS LookupType 2; or using an extension table (GPOS LookupType 9):
		if lookup.LookupType not in [2, 9]:
			print "This is not a pair adjustment positioning lookup (GPOS LookupType 2); or using an extension table (GPOS LookupType 9)."
			return
		
		# Step through each subtable
		for subtableItem in lookup.SubTable:
			if subtableItem.LookupType == 2: # normal case, not using extension table
				pairPos = subtableItem
			elif subtableItem.LookupType == 9: # extension table
				pairPos = subtableItem.ExtSubTable
			
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
						
#						glyphPairsList.append((firstGlyphsList[pairSetIndex], secondGlyph, kernValue))
						glyphPairsDict[(firstGlyphsList[pairSetIndex], secondGlyph)] = kernValue


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
								for l in leftClasses[record].glyphs:
									for r in rightClasses[j].glyphs:
	#									print l, r, kernValue
#										glyphPairsList.append((l, r, kernValue))
										if (l, r) in glyphPairsDict:
											continue
										else:
											glyphPairsDict[(l, r)] = kernValue
							
						else:
							print 'ERROR'

# 	print '-' * 80
# 	for i in sorted(glyphPairsDict.keys()):
# 		print i[0], i[1], glyphPairsDict[i]
# 	print
# 	print len(glyphPairsDict)
	
	for pair, value in glyphPairsDict.items():
	 	li.append('KPX %s %s %s' % ( pair[0], pair[1], value ))
			
	li.sort()
	output = '\n'.join(li)
	scrap = os.popen('pbcopy', 'w')
	scrap.write(output)
	scrap.close()
	print 'done'


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