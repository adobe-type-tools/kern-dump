#!/usr/bin/env python3

from getKerningPairsFromFEA import FEAKernReader
from getKerningPairsFromOTF import OTFKernReader
from getKerningPairsFromUFO import UFOkernReader
from pathlib import Path
import defcon
import argparse


def dumpKerning(kernDict, fileName):
    output = [f"{g_1} {g_2} {value}" for (g_1, g_2), value in sorted(kernDict.items())]
    with open(fileName, "w") as blob:
        blob.write('\n'.join(output))


def extractKerning(input_file):
    if input_file.suffix in [".ttf", ".otf"]:
        otfKern = OTFKernReader(input_file)
        return otfKern.kerningPairs
    elif input_file.suffix == ".ufo":
        ufoKern = UFOkernReader(defcon.Font(input_file), includeZero=True)
        return ufoKern.allKerningPairs
    else:
        # assume .fea
        feaOrgKern = FEAKernReader(input_file)
        return feaOrgKern.flatKerningPairs


def get_args(args=None):
    parser = argparse.ArgumentParser(
        description=(
            'Extract (flat) kerning from ufo, ttf, '
            'otf or fea and write it to a text file.')
    )
    parser.add_argument(
        'sourceFiles',
        nargs='+',
        metavar='SOURCE',
        help='source file(s) to extract kerning from'
    )
    parser.add_argument(
        '-o', '--output',
        dest='outputDir'
    )

    args = parser.parse_args(args)


def main(args=None):

    args = get_args()
    for source in args.sourceFiles:
        input_file = Path(source)
        output_file = input_file.with_suffix(".kerndump")

        print(f"extracting kerning from {input_file.name}")
        kerning = extractKerning(input_file)
        if args.outputDir:
            output_dir = Path(args.outputDir)
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / output_file.name

        dumpKerning(kerning, output_file)


if __name__ == "__main__":
    main()
