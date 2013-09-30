import sys
import os
import re
import itertools

'''

Takes feature file, returns python KerningClass class for each kern class found within that file.
KerningClass object has .glyphs, .side, .name attributes.

---------
2013-09-25 
Added support to read all kerning pairs from feature file.
This is a first, quite rough implementation since it does not care for kern values assigned in duplicate, or about enumerated pairs.

2013-09-26
More detailed version, taking care of enum, GOADB.

'''


class KerningClass(object):
    def __init__(self):
        self.glyphs = []
        self.name = ''
        self.side = ''


class KernFeatureReader(object):

    def __init__(self, options):
        
        self.goadbPath = None
        self.options = options

        if "-go" in self.options:
            self.goadbPath =  self.options[self.options.index('-go')+1]

        self.featureFilePath = self.options[-1]

        self.featureData = self.readFile(self.featureFilePath)
        self.kernClasses = self.readKernClasses()

        self.singleKerningPairs = {}
        self.classKerningPairs = {}
        self.allKerningPairs = self.makePairDicts()

        if self.goadbPath:
            self.glyphNameDict = {}
            self.readGOADB()
            self.allKerningPairs = self.convertNames(self.allKerningPairs)


        self.outputlist = []
        for (left, right), value in self.allKerningPairs.items():
            self.outputlist.append('/%s /%s %s' % (left, right, value))
        self.outputlist.sort()



    def readFile(self, filePath):
        # removes raw file minus commented lines
        lineList = []
        inputfile = open(filePath, 'r')
        for line in inputfile:
            if not line.strip().startswith('#'):
                lineList.append(line)
        fileLinesString = '\n'.join(lineList)
        
        inputfile.close()
        return fileLinesString


    def convertNames(self, pairDict):
        newPairDict = {}
        for (left, right), value in pairDict.items():
            newLeft = self.glyphNameDict.get(left)
            newRight = self.glyphNameDict.get(right)

            # in case the glyphs are not in the GOADB:
            if not newLeft:
                newLeft = left
            if not newRight:
                newRight = right
            
            newPair = (newLeft, newRight)
            newPairDict[newPair] = value
            # print left, right, value
        return newPairDict


    def readKernClasses(self):
        allClassesList = re.findall(r"(@\S+)\s*=\s*\[([ A-Za-z0-9_.]+)\]\s*;", self.featureData)

        classes = {}
        for name, glyphs in allClassesList:
            classes[name] = glyphs.split()

            # c = KerningClass()
            # c.name = name
            # c.glyphs = glyphs.split()

            # if name.split('_')[-1] == 'LEFT':
            #     c.side = 'LEFT'
            #     classes[c.name] = c
            # elif name.split('_')[-1] == 'RIGHT':
            #     c.side = 'RIGHT'
            #     classes[c.name] = c

            # else:
            #     c.side = 'BOTH'
            #     classes[c.name] = c

            #     # d = KerningClass()
            #     # d.name = c.name
            #     # d.glyphs = c.glyphs
            #     # d.side = 'RIGHT'
            #     # classes[d.name] = d
            
        return classes


    def allCombinations(self, left, right):
        leftGlyphs = self.kernClasses.get(left, [left])
        rightGlyphs = self.kernClasses.get(right, [right])
        
        combinations = list(itertools.product(leftGlyphs, rightGlyphs))
        return combinations


    def makePairDicts(self):
        givenKerningPairs = re.findall(r"\s*(enum )?pos (.+?) (.+?) (-?\d+?);", self.featureData)
        # reads commented lines!! Fix!
        allKerningPairs = {}
        for loop, (enum, left, right, value) in enumerate(givenKerningPairs):
            leftGlyphs = [left]
            rightGlyphs = [right]

            if enum:
                # shorthand for single pairs
                for combo in self.allCombinations(left, right):
                    self.singleKerningPairs[combo] = value

            elif not '@' in left and not '@' in right:
                self.singleKerningPairs[(left, right)] = value

            else:
                for combo in self.allCombinations(left, right):
                    self.classKerningPairs[combo] = value

            # if self.convertGlyphNames:
            #     leftGlyphs = [self.glyphNameDict.get(gName) for gName in leftGlyphs]
            #     rightGlyphs = [self.glyphNameDict.get(gName) for gName in rightGlyphs]


        allKerningPairs.update(self.classKerningPairs)
        allKerningPairs.update(self.singleKerningPairs) # overwrites any given class kern values with exceptions.

        return allKerningPairs


    def readGOADB(self):
        goadbData = self.readFile(self.goadbPath)
        allNamePairs = re.findall(r"(\S+?)\t(\S+?)(\t\S+?)?\n", goadbData)

        for finalName, workingName, override in allNamePairs:
            self.glyphNameDict[workingName] = finalName



if len(sys.argv) > 1:

    options = sys.argv[1:]
    kernFile = options[-1]

    if os.path.exists(kernFile) and os.path.splitext(kernFile)[-1] in ['.fea', '.kern']:
        kfr=KernFeatureReader(options)

        # print kfr.allKerningPairs
        # print len(kfr.singleKerningPairs)
        # print len(kfr.classKerningPairs)

        print '\n'.join(kfr.outputlist)
        print len(kfr.allKerningPairs)

    else:
        print "No valid kern feature file provided."

else:
    print "No valid kern feature file provided."

