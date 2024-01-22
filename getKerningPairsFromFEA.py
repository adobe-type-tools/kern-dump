#!/usr/bin/env python3
'''
Print all kerning pairs to be expected from a kern feature file.
This script has the ability to use a GlyphOrderAndAliasDB file for translating
"friendly" glyph names to final glyph names (for comparison with OTF).
'''


import argparse
import itertools
import re


# Regular expressions for parsing individual kerning commands:
x_range_range = re.compile(
    r'\s*(enum\s+?)?pos\s+?\[\s*(.+?)\s*\]\s+?\[\s*(.+?)\s*\]\s+?<?(-?\d+?)( 0 \4 0>)?\s*;')
x_range_glyph = re.compile(
    r'\s*(enum\s+?)?pos\s+?\[\s*(.+?)\s*\]\s+?(.+?)\s+?<?(-?\d+?)( 0 \4 0>)?\s*;')
x_glyph_range = re.compile(
    r'\s*(enum\s+?)?pos\s+?(.+?)\s+?\[\s*(.+?)\s*\]\s+?<?(-?\d+?)( 0 \4 0>)?\s*;')
x_item_item = re.compile(
    r'\s*(enum\s+?)?pos\s+?(.+?)\s+?(.+?)\s+?<?(-?\d+?)( 0 \4 0>)?\s*;')


x_lookup_start = re.compile(
    r'\s*lookup .+? {\s*')
x_lookup_flag = re.compile(
    r'\s*lookupflag .+?')
x_lookup_end = re.compile(
    r'\s*} .+?;\s*')
x_subtable_break = re.compile(
    r'\s*subtable;')


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
            line = f'{left} {right} {value}'
            self.output.append(line)
        self.output.sort()

    def readFile(self, filePath):
        # reads raw file, removes commented lines
        filtered_lines = []
        with open(filePath, 'r') as inputfile:
            data = inputfile.read().splitlines()

        for line in data:
            if '#' in line:
                # remove # and everything after -- supporting in-line comments
                line = line.split('#')[0].strip()
            if line:
                filtered_lines.append(line)

        return '\n'.join(filtered_lines)

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
        leftGlyphs = self.kernClasses.get(left, [left])
        rightGlyphs = self.kernClasses.get(right, [right])

        combinations = list(itertools.product(leftGlyphs, rightGlyphs))
        return combinations

    def parseKernLines(self):
        '''
        Read the individual lines of the kern feature, and break them down
        into kerning pairs. This means (for example) that a line like
        pos [ a b ] c -10;
        will be broken down into the pairs a c and b c.
        '''
        featureLines = self.featureData.splitlines()
        rxs_ignore = [x_lookup_start, x_lookup_end, x_lookup_flag, x_subtable_break]
        rxs_expression = [x_range_range, x_range_glyph, x_glyph_range]

        foundKerningPairs = []
        for line_index, line in enumerate(featureLines):
            if '[' in line:  # line contains a range
                for rx_expression in rxs_expression:
                    match = re.match(rx_expression, line)
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
                    if any([re.match(m, line) for m in rxs_ignore]):
                        pass
                    else:
                        print(f'cannot match line\n"{line}"\n')
        return foundKerningPairs

    def makeFlatPairs(self):
        indexedPairs = {}
        flatKerningPairs = {}

        for pIndex, (enum, pair, value_str) in enumerate(self.foundKerningPairs):
            left = pair[0]
            right = pair[1]

            if enum:
                # `enum` is shorthand for breaking down a one-line
                # command into multiple single pairs
                pairList = self.allCombinations(left, right)

            elif '@' not in left and '@' not in right:
                # glyph-to-glyph kerning
                pairList = [pair]

            else:
                # class-to-class, class-to-glyph, or glyph-to-class kerning
                pairList = self.allCombinations(left, right)

            indexedPairs[pIndex] = KerningPair(pair, pairList, int(value_str))

        # Iterate through the kerning pairs in reverse order to
        # overwrite less specific pairs with more specific ones:
        for pIndex, kerningPair in sorted(indexedPairs.items(), reverse=True):
            for pair in kerningPair.pairList:
                flatKerningPairs[pair] = kerningPair.value

        return flatKerningPairs

    def readGOADB(self, goadbPath):
        goadb_dict = {}
        goadb_list = self.readFile(goadbPath).splitlines()

        for line in goadb_list:
            if not line.strip().startswith('#'):  # get rid of comments
                chunks = line.split()
                if len(chunks) < 2:
                    print(
                        f'Something is wrong with this GOADB line:\n'
                        f'"{line}"')
                else:
                    final_name, friendly_name = chunks[0], chunks[1]
                    goadb_dict[friendly_name] = final_name
        return goadb_dict


def get_args(args=None):

    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        'feature_file',
        metavar='FEA',
        help='feature file',
    )
    parser.add_argument(
        'goadb_file',
        metavar='GOADB',
        nargs='?',
        default=None,
        help='goadb file (optional)',
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = get_args()
    kfr = FEAKernReader(args.feature_file, args.goadb_file)
    print('\n'.join(kfr.output) + '\n')
    print('Total amount of kerning pairs:', len(kfr.flatKerningPairs))
