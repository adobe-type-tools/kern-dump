#!/usr/bin/env python3
'''
Print a list of all kerning pairs to be expected from a kern feature file.
The feature file has to be passed to the script as an argument.
This script has the ability to use a GlyphOrderAndAliasDB file for translating
"friendly" glyph names to final glyph names (for comparison with OTF).
'''


import argparse
import itertools
import re


# Regular expressions for parsing individual kerning commands:
x_range_range = re.compile(
    r'\s*(enum\s+?)?pos\s+?\[\s*(.+?)\s*\]\s+?\[\s*(.+?)\s*\]\s+?(-?\d+?)\s*;')
x_range_glyph = re.compile(
    r'\s*(enum\s+?)?pos\s+?\[\s*(.+?)\s*\]\s+?(.+?)\s+?(-?\d+?)\s*;')
x_glyph_range = re.compile(
    r'\s*(enum\s+?)?pos\s+?(.+?)\s+?\[\s*(.+?)\s*\]\s+?(-?\d+?)\s*;')
x_item_item = re.compile(
    r'\s*(enum\s+?)?pos\s+?(.+?)\s+?(.+?)\s+?(-?\d+?)\s*;')


def flatten_glyph_list(glyph_list, group_dict):
    '''
    flatten nested lists of items (containing glyph list references)
    '''
    while any([re.match(r'@.+?', item) for item in glyph_list]):
        new_glyph_list = []
        for item in glyph_list:
            new_glyph_list.extend(group_dict.get(item, [item]))
        glyph_list = new_glyph_list

    return glyph_list


class KerningPair(object):
    '''Storing a flattened kerning pair'''

    def __init__(self, pair, pairList, value):

        self.pair = pair
        self.value = value
        self.pairList = pairList


class FEAKernReader(object):

    def __init__(self, fea_file, goadb_file=None):

        self.featureData = self.readFile(fea_file)
        self.kernClasses = self.readKernClasses()

        self.foundKerningPairs = self.parseKernLines()
        self.flatKerningPairs = self.makeFlatPairs()

        if goadb_file:
            friendlyFinalDict = self.readGOADB(goadb_file)
            self.flatKerningPairs = self.convertNames(
                self.flatKerningPairs, friendlyFinalDict)

        self.output = []
        for (left, right), value in self.flatKerningPairs.items():
            line = ' '.join([left, right, value])
            self.output.append(line)
        self.output.sort()

    def readFile(self, filePath):
        # reads raw file, removes commented lines
        lineList = []
        inputfile = open(filePath, 'r')
        data = inputfile.read().splitlines()
        inputfile.close()
        for line in data:
            if '#' in line:
                line = line.split('#')[0].strip()
            if line:
                lineList.append(line)

        lineString = '\n'.join(lineList)
        return lineString

    def convertNames(self, pairDict, friendlyFinalDict):
        newPairDict = {}
        for (left, right), value in pairDict.items():
            newLeft = friendlyFinalDict.get(left)
            newRight = friendlyFinalDict.get(right)

            # in case the glyphs are not in the GOADB:
            if not newLeft:
                newLeft = left
            if not newRight:
                newRight = right

            newPair = (newLeft, newRight)
            newPairDict[newPair] = value

        return newPairDict

    def readKernClasses(self):
        allClassesList = re.findall(
            r"(@\S+)\s*=\s*\[([ @A-Za-z0-9_.]+)\]\s*;", self.featureData)

        classes = {}
        for name, items in allClassesList:
            # at this point, classes can still contain nested classes
            classes[name] = items.split()

        # flatten nested kerning classes
        for className, itemList in classes.items():
            classes[className] = flatten_glyph_list(itemList, classes)
        return classes

    def allCombinations(self, left, right):
        if len(left.split()) > 1:
            # The left kerning object is an ad-hoc group
            # like [ a b c ] or [ a @MMK_x c ]:
            leftGlyphs = []
            leftItems = left.split()
            for item in leftItems:
                classFound = self.kernClasses.get(item, None)
                if classFound:
                    leftGlyphs.extend(classFound)
                else:
                    leftGlyphs.append(item)

        else:
            # The left kerning object is something like x or @MMK_x:
            leftGlyphs = self.kernClasses.get(left, [left])

        if len(right.split()) > 1:
            # The right kerning object is an ad-hoc group
            # like [ a b c ] or [ a @MMK_x c ]:
            rightGlyphs = []
            rightItems = right.split()
            for item in rightItems:
                classFound = self.kernClasses.get(item, None)
                if classFound:
                    rightGlyphs.extend(classFound)
                else:
                    rightGlyphs.append(item)
        else:
            # The right kerning object is something like x or @MMK_x:
            rightGlyphs = self.kernClasses.get(right, [right])

        combinations = list(itertools.product(leftGlyphs, rightGlyphs))
        return combinations

    def parseKernLines(self):
        featureLines = self.featureData.splitlines()
        foundKerningPairs = []
        for line_index, line in enumerate(featureLines):
            if '[' in line:  # line contains a range
                expressions = [x_range_range, x_range_glyph, x_glyph_range]
                for expression in expressions:
                    match = re.match(expression, line)
                    if match:
                        enum = match.group(1)
                        pair = (match.group(2), match.group(3))
                        value = match.group(4)
                        pair_combos = itertools.product(
                            pair[0].split(), pair[1].split())
                        for combo in pair_combos:
                            foundKerningPairs.append([enum, combo, value])
                        break
                    else:
                        continue
            else:  # normal item-item pair
                match = re.match(x_item_item, line)
                if match:
                    enum = match.group(1)
                    pair = (match.group(2), match.group(3))
                    value = match.group(4)
                    foundKerningPairs.append([enum, pair, value])
                else:
                    print('XXX cannot match', line)
        return foundKerningPairs

    def makeFlatPairs(self):
        indexedPairs = {}
        flatKerningPairs = {}

        for pIndex, (enum, pair, value) in enumerate(self.foundKerningPairs):
            left = pair[0]
            right = pair[1]

            if enum:
                # `enum` is shorthand for breaking down a one-line
                # command into multiple single pairs
                pairList = self.allCombinations(left, right)

            elif '@'not in left and '@' not in right:
                # glyph-to-glyph kerning
                pairList = [pair]

            else:
                # class-to-class, class-to-glyph, or glyph-to-class kerning
                pairList = self.allCombinations(left, right)

            indexedPairs[pIndex] = KerningPair(pair, pairList, value)

        # Iterate through the kerning pairs in reverse order to
        # overwrite less specific pairs with more specific ones:
        for pIndex, kerningPair in sorted(indexedPairs.items(), reverse=True):
            for pair in kerningPair.pairList:
                flatKerningPairs[pair] = kerningPair.value

        return flatKerningPairs

    def readGOADB(self, goadbPath):
        output = {}
        goadbList = self.readFile(goadbPath).splitlines()

        for line in goadbList:
            if not line.strip().startswith('#'):  # get rid of comments
                splitLine = line.split()
                if len(splitLine) < 2:
                    print('Something is wrong with this GOADB line:\n', line)
                else:
                    finalName, friendlyName = splitLine[0], splitLine[1]
                    output[friendlyName] = finalName
        return output


def get_options(args=None):

    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        'files',
        metavar='FILES',
        nargs='+',
        help='feature file, goadb file (optional)',
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = get_options()

    goadb_file = None
    if len(args.files) == 2:
        fea_file, goadb_file = args.files
    else:
        fea_file = args.files[0]

    kfr = FEAKernReader(fea_file, goadb_file)
    print('\n'.join(kfr.output) + '\n')
    print('Total amount of kerning pairs:', len(kfr.flatKerningPairs))
