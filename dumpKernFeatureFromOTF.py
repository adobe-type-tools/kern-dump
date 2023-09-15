#!/usr/bin/env python3
import argparse
import os
import string
from importlib import reload
from pathlib import Path

import getKerningPairsFromOTF
reload(getKerningPairsFromOTF)

__doc__ = '''

    This script extracts a viable kern feature file from a compiled OTF.
    It requires the script 'getKerningPairsFromOTF.py'; which is distributed
    in the same folder.

    usage:
    python dumpKernFeatureFromOTF.py font.otf > outputfile

    '''

compressSinglePairs = True
# Switch to control if single pairs shall be written plainly, or in a more
# space-saving notation (using enum pos).


def sortGlyphs(glyphlist):
    # Sort glyphs in a way that glyphs from the exceptionList, or glyphs
    # starting with 'uni' names do not get to be key (first) glyphs.
    # An infinite loop is avoided, in case there are only glyphs matching
    # above mentioned properties.
    exceptionList = 'dotlessi dotlessj kgreenlandic ae oe AE OE uhorn'.split()

    glyphs = sorted(glyphlist)
    for i in range(len(glyphs)):
        if glyphs[0] in exceptionList or glyphs[0].startswith('uni'):
            glyphs.insert(len(glyphs), glyphs.pop(0))
        else:
            continue

    return glyphs


def nameClass(glyphlist, flag):
    glyphs = sortGlyphs(glyphlist)
    if len(glyphs) == 0:
        name = 'error!!!'
    else:
        name = glyphs[0]

    if name in string.ascii_lowercase:
        case = '_LC'
    elif name in string.ascii_uppercase:
        case = '_UC'
    else:
        case = ''

    flag = flag

    return f'@{name}{flag}{case}'


def buildOutputList(sourceList, outputList, headlineString):
    if len(sourceList):
        headline = headlineString
        decoration = '-' * len(headline)

        outputList.append('# ' + headline)
        outputList.append('# ' + decoration)

        for item in sourceList:
            outputList.append(item)
        outputList.append('')


def makeKernFeature(fontPath):
    okr = getKerningPairsFromOTF.OTFKernReader(fontPath)
    allClasses = {}
    classList = []
    fea_output = []

    for kerningClass in okr.allLeftClasses:
        glyphs = sortGlyphs(okr.allLeftClasses[kerningClass])
        className = nameClass(glyphs, '_LEFT')
        allClasses.setdefault(className, glyphs)

    for kerningClass in okr.allRightClasses:
        glyphs = sortGlyphs(okr.allRightClasses[kerningClass])
        className = nameClass(glyphs, '_RIGHT')
        allClasses.setdefault(className, glyphs)

    singlePairsList = sorted(okr.singlePairs.items())

    classPairsList = []
    for (leftClass, rightClass), value in sorted(okr.classPairs.items()):
        leftGlyphs = sortGlyphs(okr.allLeftClasses[leftClass])
        leftClassName = nameClass(leftGlyphs, '_LEFT')

        rightGlyphs = sortGlyphs(okr.allRightClasses[rightClass])
        rightClassName = nameClass(rightGlyphs, '_RIGHT')

        classPairsList.append(((leftClassName, rightClassName), value))

    for className in sorted(allClasses):
        glyphs = allClasses[className]
        classList.append(f'{className} = [ {" ".join(glyphs)} ];')

    buildOutputList(
        [], fea_output, f'kern feature dumped from {os.path.basename(fontPath)}')
    buildOutputList(
        classList, fea_output, 'kerning classes')

    if compressSinglePairs:

        leftGlyphsDict = {}
        rightGlyphsDict = {}

        compressedLeft = []
        compressedBoth = []

        class_glyph = []
        glyph_class = []
        glyph_glyph = []
        exploding_class_class = []

        # Compress the single pairs to a more space-saving notation.
        # First, dictionaries for each left glyph are created.
        # If the kerning value to any right glyph happens to be equal,
        # those right glyphs are merged into a 'class'.

        for (left, right), value in singlePairsList:
            leftGlyph = left
            leftGlyphsDict.setdefault(leftGlyph, {})
            kernValueDict = leftGlyphsDict[leftGlyph]
            kernValueDict.setdefault(value, []).append(right)

        for left in leftGlyphsDict:
            for value in leftGlyphsDict[left]:
                right = leftGlyphsDict[left][value]
                right = sortGlyphs(right)
                compressedLeft.append((left, right, value))

        # Same happens for the right side; including classes that
        # have been compressed before.

        for left, right, value in compressedLeft:
            rightGlyph = ' '.join(right)
            rightGlyphsDict.setdefault(rightGlyph, {})
            kernValueDict = rightGlyphsDict[rightGlyph]
            kernValueDict.setdefault(value, []).append(left)

        for right in rightGlyphsDict:
            for value in rightGlyphsDict[right]:
                left = rightGlyphsDict[right][value]
                left = sortGlyphs(left)
                compressedBoth.append((left, right.split(), value))

        # Splitting the compressed single-pair kerning into four different
        # lists; organized by type:

        for left, right, value in compressedBoth:
            left_items = ' '.join(left)
            right_items = ' '.join(right)
            if len(left) != 1 and len(right) != 1:
                exploding_class_class.append(
                    f'enum pos [ {left_items} ] [ {right_items} ] ;')
            elif len(left) != 1 and len(right) == 1:
                class_glyph.append(
                    f'enum pos [ {left_items} ] {right_items} {value};')
            elif len(left) == 1 and len(right) != 1:
                glyph_class.append(
                    f'enum pos {left_items} [ {right_items} ] {value};')
            elif len(left) == 1 and len(right) == 1:
                glyph_glyph.append(
                    f'pos {left_items} {right_items} {value};')
            else:
                print(f'ERROR with ({" ".join(left, right, value)})')

        # Making sure all the pairs made it through the process:
        if len(compressedBoth) != (
            len(class_glyph) + len(glyph_class) +
            len(glyph_glyph) + len(exploding_class_class)
        ):
            print('ERROR - we lost some kerning pairs.')

        buildOutputList(glyph_glyph, fea_output, 'glyph to glyph')
        buildOutputList(glyph_class, fea_output, 'glyph to class')
        buildOutputList(class_glyph, fea_output, 'class to glyph')
        buildOutputList(
            exploding_class_class, fea_output,
            'exploding class to exploding class')

    else:
        # Plain list of single pairs
        glyph_glyph = []
        for (left, right), value in singlePairsList:
            glyph_glyph.append(f'pos {left} {right} {value};')

        buildOutputList(glyph_glyph, fea_output, 'glyph to glyph')

    # List of class-to-class pairs
    class_class = []
    for (left, right), value in classPairsList:
        class_class.append(f'pos {left} {right} {value};')

    buildOutputList(class_class, fea_output, 'class to class')
    return fea_output


def get_args(args=None):

    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        'font_file',
        metavar='FONT',
        help='font file',
    )
    return parser.parse_args(args)


def main():
    args = get_args()
    font_path = Path(args.font_file)
    if font_path.exists() and font_path.suffix in ['.otf', '.ttf']:
        fea = makeKernFeature(font_path)
        print('\n'.join(fea))


if __name__ == "__main__":
    main()
