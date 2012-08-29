import os, sys
import inspect
from fontTools import ttLib
import fontTools

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
		# print featRecItem.FeatureTag  # GPOS feature tags (e.g. kern, mark, mkmk, size) of each ScriptRecord
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
	# featureCount = featureList.FeatureCount # integer
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
			# print subtableItem.LookupType
			# print subtableItem.ExtensionLookupType
			if subtableItem.LookupType == 2: # normal case, not using extension table
				pairPos = subtableItem
			elif subtableItem.LookupType == 9: # extension table
				# print subtableItem.ExtensionLookupType
				# print subtableItem.ExtSubTable
				if subtableItem.ExtensionLookupType == 8:
					continue
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
			
			if pairPos.Format == 1:  # glyph pair adjustment; format 2 is class pair adjustment
			
				# This iteration is done by index so that we have a way to reference the firstGlyphsList list
				for pairSetIndex in range(len(pairPos.PairSet)):
						# print 'xxx', len(pairPos.PairSet), 'xxx'
					for pairValueRecordItem in pairPos.PairSet[pairSetIndex].PairValueRecord:
						secondGlyph = pairValueRecordItem.SecondGlyph
						kernValue = pairValueRecordItem.Value1.XAdvance
						
						glyphPairsDict[(firstGlyphsList[pairSetIndex], secondGlyph)] = kernValue
						
						print kernValue
				
				
				
				



if __name__ == "__main__":
	if len(sys.argv) == 2:
		if os.path.exists(sys.argv[1]):
			fontPath = sys.argv[1]
    		main(fontPath)
	else:
		print "No valid font provided."