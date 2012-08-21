import os, sys
import inspect
from fontTools import ttLib

kKernFeatureTag = 'kern'


class myLeftGlyph:
	def __init__(self, glyphName, kernPartner):
		self.glyphName = glyphName
		self.kernPartner = kernPartner


class myRightGlyph:
	def __init__(self, glyphName, kernRecord, kernValue):
		self.glyphName = glyphName
		self.kernRecord = kernRecord
		self.kernValue = kernValue



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
						
						glyphPairsList.append((firstGlyphsList[pairSetIndex], secondGlyph, kernValue))

			elif pairPos.Format == 2: # class adjustment
				firstGlyphs = {}
				secondGlyphs = {}
				secondGlyphList = []
#				print firstGlyphsList

				# Find left glyphs kerned to Class2Record index="1".
				# This class is weirdly mixed and has no class="X" property, that is why we have to find them that way. 
				for leftGlyph in firstGlyphsList:
					if not leftGlyph in pairPos.ClassDef1.classDefs:
						kernPartner = 1
						firstGlyphs[leftGlyph] = kernPartner
						lg = myLeftGlyph(leftGlyph, kernPartner)
						firstGlyphs[leftGlyph] = lg

 				for leftGlyph in pairPos.ClassDef1.classDefs:
 					kernPartner = pairPos.ClassDef1.classDefs[leftGlyph] + 1
					lg = myLeftGlyph(leftGlyph, kernPartner)
					firstGlyphs[leftGlyph] = lg
					
# 				print firstGlyphs
				
# 					print pairPos.ClassDef1.classDefs[g]

				for secondGlyph in pairPos.ClassDef2.classDefs:					
 					record = pairPos.ClassDef2.classDefs[secondGlyph]
 					print secondGlyph, record#, pairPos.Class1Record[record]

#  					for i in pairPos.Class1Record:
#  						print pairPos.Class1Record.index(i)
#  						print i.Class2Record[record].Value1.XAdvance

#					kernValue = pairPos.Class1Record[record].Class2Record[record].Value1.XAdvance
					kernValue = pairPos.Class1Record[0].Class2Record[record].Value1.XAdvance
					sg = myRightGlyph(secondGlyph, record, kernValue)

					if record in secondGlyphs:
						secondGlyphs[record].append( sg )
					else:
						secondGlyphs[record] = [ sg ]
				
# 				for i in secondGlyphs:
# 					print [j.glyphName for j in secondGlyphs[i]]
					
				for i in firstGlyphs:
					kp = firstGlyphs[i].kernPartner
					if kp in secondGlyphs.keys():
						for j in secondGlyphs[kp]:
#	 						print firstGlyphs[i].glyphName, j.glyphName, j.kernValue
	 						glyphPairsList.append((firstGlyphs[i].glyphName, j.glyphName, j.kernValue))
					else:
						print kp, 'not found' 

#					print i.glyphName
#					firstGlyphs[i].kernPartner
# 					print g
#					secondGlyphList.append(sg)
# 					if record in secondGlyphs:
# 						secondGlyphs[record].append(secondGlyph)
# 					else:
# 						secondGlyphs[record] = [secondGlyph]
# 					record = pairPos.ClassDef2.classDefs[secondGlyph]
# 					print secondGlyph, record
#					kernValue = pairPos.Class1Record[record-1].Class2Record[record].Value1.XAdvance
#					print secondGlyph, kernValue

# 				for i in secondGlyphList:
# 					print i.glyphName, i.kernValue
				
				
#  				for g in pairPos.ClassDef1.classDefs:
#  					for secondGlyph in pairPos.ClassDef2.classDefs:
#  						record = pairPos.ClassDef2.classDefs[secondGlyph]
#  						print g, secondGlyph, record

#						print record
# 						for i in pairPos.Class1Record:
# 							print leftGlyph, secondGlyph, 
# 							 Class2Record[record].Value1.XAdvance
#						kernValue = pairPos.Class1Record[record-1].Class2Record[record].Value1.XAdvance
#						kernValue = pairPos.Class1Record[0].Class2Record[record].Value1.XAdvance
					

#						glyphPairsList.append((leftGlyph, secondGlyph, kernValue))
					
					
#					kernValue = 
# 				print pairPos.Class1Record[0].Class2Record[1].Value1.XAdvance

# 				print pairPos.ClassDef2.classDefs.items()
# 				for i in pairPos.Class1Record:
# 					print i.Class2Record[1].Value1.XAdvance
#  				print pairPos.Class1Record
# 				print pairPos.Class2Count
#  				print pairPos.ValueFormat2
				
				
	print '-' * 80
	print len(glyphPairsList), glyphPairsList



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