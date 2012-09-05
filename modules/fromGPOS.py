import os, sys, string, time
from fontTools import ttLib
from tools import *

# import inspect
# from operator import itemgetter

__doc__ ='''\

	This is a module for extracting kerning information from compiled fonts; which is happening via TTX.
	
	'''

class myLeftClass:
	def __init__(self):
		self.glyphs = []
		self.class1Record = 0


class myRightClass:
	def __init__(self):
		self.glyphs = []
		self.class2Record = 0



def collectUniqueKernLookupListIndexes(featureRecord):
	kKernFeatureTag = 'kern'
	uniqueKernLookupListIndexesList = []
	for featRecItem in featureRecord:
		# print featRecItem.FeatureTag  # GPOS feature tags (e.g. kern, mark, mkmk, size) of each ScriptRecord
		if featRecItem.FeatureTag == kKernFeatureTag:
			feature = featRecItem.Feature
		
			for featLkpItem in feature.LookupListIndex:
				if featLkpItem not in uniqueKernLookupListIndexesList:
					uniqueKernLookupListIndexesList.append(featLkpItem)

	return uniqueKernLookupListIndexesList


def getPairPos(fontPath):
	output = []
	font = ttLib.TTFont(fontPath)
	gposTable = font['GPOS'].table

	classPairsList	= []
	allClasses = {}

	### ScriptList ###
	# scriptList = gposTable.ScriptList

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
					continue # no solution for contextual kerning pairs right now.

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
			output.append(pairPos)

	return output
			# return pairPos, firstGlyphsList

	
#		return singlePairsList

def getSinglePairs(fontPath):
	singlePairsList = []
	for pairPos in getPairPos(fontPath):
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

	return singlePairsList

def getClassPairs(fontPath, option = None):
	classPairsList	= []
	allClasses = {}

	for pairPos in getPairPos(fontPath):
		firstGlyphsList = pairPos.Coverage.glyphs
		if pairPos.Format == 2: # class adjustment
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
								continue
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
				
	if not option:
		return classPairsList, 

	else:
		return allClasses
	
def getClasses(fontPath):
	return getClassPairs(fontPath, 'option')

# if __name__ == "__main__":
# 	startTime = time.time()
# 	
# 	if len(sys.argv) == 2:
# 		if os.path.exists(sys.argv[1]):
# 			fontPath = sys.argv[1]
#     		single(fontPath)
# 	else:
# 		print "No valid font provided."
# 	endTime = round(time.time() - startTime, 2)
# 	print endTime, 'seconds'
