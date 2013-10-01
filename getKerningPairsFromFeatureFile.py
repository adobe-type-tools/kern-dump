import sys
import os
import re
import itertools


__doc__ = '''\

Prints a list of all kerning pairs to be expected from a kern feature file; which has to be passed to the script as an argument.
Has the ability to use a GlyphOrderAndAliasDB file for translation of working glyph names to final glyph names.

Usage:
------
python getKerningPairsFromFeatureFile.py <path to kern feature file>
python getKerningPairsFromFeatureFile.py -go <path to GlyphOrderAndAliasDB file> <path to kern feature file>


'''


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


        self.output = []
        for (left, right), value in self.allKerningPairs.items():
            self.output.append('/%s /%s %s' % (left, right, value))
        self.output.sort()



    def readFile(self, filePath):
        # reads raw file, removes commented lines
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

        return newPairDict


    def readKernClasses(self):
        allClassesList = re.findall(r"(@\S+)\s*=\s*\[([ A-Za-z0-9_.]+)\]\s*;", self.featureData)

        classes = {}
        for name, glyphs in allClassesList:
            classes[name] = glyphs.split()

        return classes


    def allCombinations(self, left, right):
        leftGlyphs = self.kernClasses.get(left, [left])
        rightGlyphs = self.kernClasses.get(right, [right])
        
        combinations = list(itertools.product(leftGlyphs, rightGlyphs))
        return combinations


    def makePairDicts(self):
        givenKerningPairs = re.findall(r"\s*(enum )?pos (.+?) (.+?) (-?\d+?);", self.featureData)
        allKerningPairs = {}
        for loop, (enum, left, right, value) in enumerate(givenKerningPairs):
            if enum:
                # shorthand for single pairs
                for combo in self.allCombinations(left, right):
                    self.singleKerningPairs[combo] = value

            elif not '@' in left and not '@' in right:
                self.singleKerningPairs[(left, right)] = value

            else:
                for combo in self.allCombinations(left, right):
                    self.classKerningPairs[combo] = value


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

        print '\n'.join(kfr.output)
        print len(kfr.allKerningPairs)

    else:
        print "No valid kern feature file provided."

else:
    print "No valid kern feature file provided."

