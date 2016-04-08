#!/usr/bin/env python

import os
import defcon
from getKerningPairsFromFEA import KernFeatureReader as FeaKernReader
from getKerningPairsFromOTF import ReadKerning as OTFKernReader
from getKerningPairsFromUFO import UFOkernReader


def dumpKerning(kernDict, fileName):
    f = open(fileName, "w")
    for (g1, g2), v in sorted(kernDict.items()):
        f.write("%s %s %s\n" % (g1, g2, v))
    f.close()


def extractKerning(path):
    path = os.path.normpath(path)  # remove trailing slash for .ufo
    base, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in [".ttf", ".otf"]:
        otfKern = OTFKernReader(path)
        return otfKern.kerningPairs
    elif ext == ".ufo":
        ufoKern = UFOkernReader(defcon.Font(path), includeZero=True)
        return ufoKern.allKerningPairs
    else:
        # assume .fea
        feaOrgKern = FeaKernReader([path])
        return feaOrgKern.flatKerningPairs


def main(args):
    import argparse

    parser = argparse.ArgumentParser(description='Extract (flat) kerning from ufo, ttf, otf or fea and write it to a text file.')
    parser.add_argument('sourceFiles', nargs='+', metavar="SOURCE",
                       help='source files to extract kerning from')
    parser.add_argument('-o', '--output', dest='outputFolder')

    args = parser.parse_args(args)
    for source in args.sourceFiles:
        print "extracting kerning from", source
        kerning = extractKerning(source)
        output = os.path.normpath(source) + ".kerndump"
        if args.outputFolder:
            output = os.path.join(args.outputFolder, os.path.basename(output))
        dumpKerning(kerning, output)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
