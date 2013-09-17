import os, sys
#import inspect
from fontTools import ttLib

'''
Gets all possible kerning pairs within font.
Supports RTL.

2013-01-22:
Working with Bickham Script pro 3 and its many subtables, it was discovered that 
the script reports many more pairs than actually exist. Investigate!

'''

kKernFeatureTag = 'kern'
kGPOStableName = 'GPOS'
finalList = []
# AFMlist = []


class myLeftClass:
    def __init__(self):
        self.glyphs = []
        self.class1Record = 0

class myRightClass:
    def __init__(self):
        self.glyphs = []
        self.class2Record = 0


def collectUniqueKernLookupListIndexes(featureRecord):
    uniqueKernLookupIndexList = []
    for featRecItem in featureRecord:
        # print featRecItem.FeatureTag  # GPOS feature tags (e.g. kern, mark, mkmk, size) of each ScriptRecord
        if featRecItem.FeatureTag == kKernFeatureTag:
            feature = featRecItem.Feature

            for featLookupItem in feature.LookupListIndex:
                if featLookupItem not in uniqueKernLookupIndexList:
                    uniqueKernLookupIndexList.append(featLookupItem)
    
    return uniqueKernLookupIndexList


def getPairKerning():
    pass

def getClassKerning():
    pass


def run(fontPath):
    font = ttLib.TTFont(fontPath)
    
    if kGPOStableName not in font:
        print "The font has no %s table" % kGPOStableName
        return
    
    gposTable = font[kGPOStableName].table
    glyphPairsDict = {}
    
    # 'ScriptList:'
    # scriptList = gposTable.ScriptList

    'FeatureList:'
    featureList = gposTable.FeatureList
    # featureCount = featureList.FeatureCount # integer
    featureRecord = featureList.FeatureRecord
    
    uniqueKernLookupIndexList = collectUniqueKernLookupListIndexes(featureRecord)
    
    # Make sure a 'kern' feature was found:
    if not len(uniqueKernLookupIndexList):
        print "The font has no %s feature" % kKernFeatureTag
        return

    'LookupList:'
    lookupList = gposTable.LookupList
    for kernLookupIndex in sorted(uniqueKernLookupIndexList):
        lookup = lookupList.Lookup[kernLookupIndex]
        
        '''
        1   Single adjustment           Adjust position of a single glyph
        2   Pair adjustment             Adjust position of a pair of glyphs
        3   Cursive attachment          Attach cursive glyphs
        4   MarkToBase attachment       Attach a combining mark to a base glyph
        5   MarkToLigature attachment   Attach a combining mark to a ligature
        6   MarkToMark attachment       Attach a combining mark to another mark
        7   Context positioning         Position one or more glyphs in context
        8   Chained Context positioning Position one or more glyphs in chained context
        9   Extension positioning       Extension mechanism for other positionings
        10+ Reserved                    For future use
        '''


        # Confirm this is a GPOS LookupType 2; or using an extension table (GPOS LookupType 9):
        if lookup.LookupType not in [2, 9]:
            print "This is not a pair adjustment positioning lookup (GPOS LookupType 2); or using an extension table (GPOS LookupType 9)."
            continue
        
        # Step through each subtable
        for subtableItem in lookup.SubTable:
            if subtableItem.LookupType == 2: # normal case, not using extension table
                pairPos = subtableItem
            elif subtableItem.LookupType == 9: # extension table
                if subtableItem.ExtensionLookupType == 8: # contextual
                    continue
                elif subtableItem.ExtensionLookupType == 2:
                    pairPos = subtableItem.ExtSubTable
            
            if pairPos.Coverage.Format not in [1, 2]:
                print "WARNING: Coverage format %d is not yet supported" % pairPos.Coverage.Format
            
            if pairPos.ValueFormat1 not in [0, 4, 5]:
                print "WARNING: ValueFormat1 format %d is not yet supported" % pairPos.ValueFormat1
            
            if pairPos.ValueFormat2 not in [0]:
                print "WARNING: ValueFormat2 format %d is not yet supported" % pairPos.ValueFormat2
            
            # Each glyph in this list will have a corresponding PairSet which will
            # contain all the second glyphs and the kerning value in the form of PairValueRecord(s)
            firstGlyphsList = pairPos.Coverage.glyphs
            print firstGlyphsList
            if pairPos.Format == 1: 
            
                # This iteration is done by index so that we have a way to reference the firstGlyphsList list
                for pairSetIndex in range(len(pairPos.PairSet)):
                    for pairValueRecordItem in pairPos.PairSet[pairSetIndex].PairValueRecord:
                        secondGlyph = pairValueRecordItem.SecondGlyph
                        valueFormat = pairPos.ValueFormat1
                        if valueFormat == 5: # RTL kerning
                            kernValue = "<%d 0 %d 0>" % (pairValueRecordItem.Value1.XPlacement, pairValueRecordItem.Value1.XAdvance)
                        elif valueFormat == 0: # RTL pair with value <0 0 0 0>
                            kernValue = "<0 0 0 0>"
                        elif valueFormat == 4: # LTR kerning
                            kernValue = pairValueRecordItem.Value1.XAdvance
                        else:
                            print "\tValueFormat1 = %d" % valueFormat
                            continue # skip the rest
                        
                        glyphPairsDict[(firstGlyphsList[pairSetIndex], secondGlyph)] = kernValue


            ############################################
            ############################################
            ############################################


            elif pairPos.Format == 2: 
            # class pair adjustment
                firstGlyphs = {}
                secondGlyphs = {}

                leftClasses = {}
                rightClasses = {}
                
                # Find left class with the Class1Record index="0".
                # This class is weirdly mixed into the "Coverage" (e.g. all left glyphs) 
                # and has no class="X" property, that is why we have to find them that way. 
                
                ## I THINK THE BUG IS IN HERE!
                ###### XXXXXX

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
                    

                
                # for i in rightClasses:
                #     print rightClasses[i].class2Record, sorted(rightClasses[i].glyphs)

                for record_l in leftClasses:
                    for record_r in rightClasses:
                        if pairPos.Class1Record[record_l].Class2Record[record_r]:
                            valueFormat = pairPos.ValueFormat1
                            
                            if valueFormat in [4, 5]:
                                kernValue = pairPos.Class1Record[record_l].Class2Record[record_r].Value1.XAdvance
                            elif valueFormat == 0: # valueFormat zero is caused by a value of <0 0 0 0> on a class-class pair; skip these
                                continue
                            else:
                                print "\tValueFormat1 = %d" % valueFormat
                                continue # skip the rest
                            
                            if kernValue != 0:
                                for l in leftClasses[record_l].glyphs:
                                    for r in rightClasses[record_r].glyphs:
                                        if (l, r) in glyphPairsDict:
                                            # if the kerning pair has already been assigned in pair-to-pair kerning
                                            continue
                                        else:
                                            if valueFormat == 5: # RTL kerning
                                                kernValue = "<%d 0 %d 0>" % (pairPos.Class1Record[record_l].Class2Record[record_r].Value1.XPlacement, pairPos.Class1Record[record_l].Class2Record[record_r].Value1.XAdvance)
                                            
                                            glyphPairsDict[(l, r)] = kernValue
                            
                        else:
                            print 'ERROR'

    # print '-' * 80
    # for i in sorted(glyphPairsDict.keys()):
    #     print i[0], i[1], glyphPairsDict[i]
    # print
    # print len(glyphPairsDict)
    
    for pair, value in glyphPairsDict.items():
         finalList.append('/%s /%s %s' % ( pair[0], pair[1], value ))
        # AFMlist.append('KPX %s %s %s' % ( pair[0], pair[1], value ))
        
    finalList.sort()
    # AFMlist.sort()
    output = '\n'.join(finalList)
    # print output
    print len(output)

    # AFMoutput = '\n'.join(AFMlist)
    # scrap = os.popen('pbcopy', 'w')
    # scrap.write(AFMoutput)
    # scrap.close()
    # print 'Done. AFM copied to clipboard.'

#     scrap = os.popen('pbcopy', 'w')
#     scrap.write(output)
#     scrap.close()
#    print 'done'


#     membersList = inspect.getmembers(pairPos.ClassDef1.classDefs)
#     for x in membersList:
#         print x
#     print
#     print
    


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            fontPath = sys.argv[1]
            run(fontPath)
    else:
        print "No valid font provided."