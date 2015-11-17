#!/usr/bin/python
import os
import sys
import string
from fontTools import ttLib

import getKerningPairsFromOTF
reload(getKerningPairsFromOTF)

__doc__ ='''\

    This script extracts kerning and groups from a compiled OTF and injects
    them into a UFO file.
    It requires the script 'getKerningPairsFromOTF.py'; which is distributed
    in the same folder.

    usage:
    python dumpKernObjectFromOTF.py font.otf font.ufo

    '''


kKernFeatureTag = 'kern'
compressSinglePairs = True
# Switch to control if single pairs shall be written plainly, or in a more space-saving notation (using enum).


def sortGlyphs(glyphlist):
    # Sort glyphs in a way that glyphs from the exceptionList, or glyphs starting with 'uni' names do not get to be key (first) glyphs.
    # An infinite loop is avoided, in case there are only glyphs matching above mentioned properties.
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

    return '@MMK%s%s%s' % (flag, name, case)



def buildOutputList(sourceList, outputList, headlineString):
    # Basically just a function to create a nice headline before each chunk of kerning data.
    if len(sourceList):
        headline = headlineString
        decoration = '-'*len(headline)

        outputList.append('# ' + headline)
        outputList.append('# ' + decoration)

        for item in sourceList:
           outputList.append(item)
        outputList.append('')



def makeKernObjects(fontPath):
    f = getKerningPairsFromOTF.ReadKerning(fontPath)

    groups = {}
    kerning = {}

    for kerningClass in f.allLeftClasses:
        glyphs = sortGlyphs(f.allLeftClasses[kerningClass])
        className = nameClass(glyphs, '_L_')
        groups.setdefault(className, glyphs)

    for kerningClass in f.allRightClasses:
        glyphs = sortGlyphs(f.allRightClasses[kerningClass])
        className = nameClass(glyphs, '_R_')
        groups.setdefault(className, glyphs)


    for (leftClass, rightClass), value in sorted(f.classPairs.items()):
        leftGlyphs = sortGlyphs(f.allLeftClasses[leftClass])
        leftClassName = nameClass(leftGlyphs, '_L_')

        rightGlyphs = sortGlyphs(f.allRightClasses[rightClass])
        rightClassName = nameClass(rightGlyphs, '_R_')

        kerning[(leftClassName, rightClassName)] = value


    kerning.update(f.singlePairs)
    return groups, kerning


def injectKerningIntoUFO(ufoPath, groups, kerning):
    from defcon import Font
    ufo = Font(ufoPath)
    ufo.kerning.clear()
    ufo.groups.clear()

    print 'Injecting groups and kerning into %s ...' % ufoPath
    ufo.groups.update(groups)
    ufo.kerning.update(kerning)
    ufo.save()


errorMessage = '''\

ERROR:
No valid font and/or UFO provided.
The script is used like this:

python %s font.otf font.ufo
''' % os.path.basename(__file__)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        assumedFontPath = sys.argv[1]
        assumedUFOPath = sys.argv[2]
        assumedUFOPath = assumedUFOPath.replace('/', '')

        if  os.path.exists(assumedFontPath) and os.path.splitext(assumedFontPath)[1].lower() in ['.otf', '.ttf'] and \
            os.path.exists(assumedUFOPath) and os.path.splitext(assumedUFOPath)[1].lower() in ['.ufo']:

            fontPath = assumedFontPath
            ufoPath = assumedUFOPath
            groups, kerning = makeKernObjects(fontPath)
            injectKerningIntoUFO(ufoPath, groups, kerning)
            print 'done'

        else:
            print errorMessage

    else:
        print errorMessage
