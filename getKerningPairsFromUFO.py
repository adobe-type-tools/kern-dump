#!/usr/bin/env python3
'''
Extract a list of all (flat) kerning pairs in a UFO file’s kern object, and
report the absolute number of pairs.

'''

import argparse
import itertools
from pathlib import Path


class UFOkernReader(object):

    def __init__(self, font, includeZero=False):
        self.f = font

        try:
            format_major = self.f.ufoFormatVersionTuple[0]
        except AttributeError:
            format_major = self.f.naked().ufoFormatVersionTuple[0]

        if int(format_major) >= 3:
            self.group_indicator = 'public.'
        else:
            self.group_indicator = '@'

        self.group_group_pairs = {}
        self.group_glyph_pairs = {}
        self.glyph_group_pairs = {}
        self.glyph_glyph_pairs = {}

        self.allKerningPairs = self.makePairDicts(includeZero)
        self.output = self.makeOutput(self.allKerningPairs)

        self.totalKerning = sum(self.allKerningPairs.values())
        self.absoluteKerning = sum(
            [abs(value) for value in self.allKerningPairs.values()])

    def makeOutput(self, kerningDict):
        output = []
        for (left, right), value in kerningDict.items():
            output.append('%s %s %s' % (left, right, value))
        output.sort()
        return output

    def allCombinations(self, left, right):
        leftGlyphs = self.f.groups.get(left, [left])
        rightGlyphs = self.f.groups.get(right, [right])
        combinations = list(itertools.product(leftGlyphs, rightGlyphs))
        return combinations

    def makePairDicts(self, includeZero):
        kerningPairs = {}

        for (left, right), value in self.f.kerning.items():

            if (
                self.group_indicator in left and
                self.group_indicator in right
            ):
                # group-to-group-pair
                for combo in self.allCombinations(left, right):
                    self.group_group_pairs[combo] = value

            elif (
                self.group_indicator in left and
                self.group_indicator not in right
            ):
                # group-to-glyph-pair
                for combo in self.allCombinations(left, right):
                    self.group_glyph_pairs[combo] = value

            elif (
                self.group_indicator not in left and
                self.group_indicator in right
            ):
                # glyph-to-group-pair
                for combo in self.allCombinations(left, right):
                    self.glyph_group_pairs[combo] = value

            else:
                # glyph-to-glyph-pair a.k.a. single pair
                self.glyph_glyph_pairs[(left, right)] = value

        # The updates occur from the most general pairs to the most specific.
        # This means that any given class kerning values are overwritten with
        # the intended exceptions.
        kerningPairs.update(self.group_group_pairs)
        kerningPairs.update(self.group_glyph_pairs)
        kerningPairs.update(self.glyph_group_pairs)
        kerningPairs.update(self.glyph_glyph_pairs)

        if includeZero is False:
            # delete any kerning values == 0.
            # This cannot be done in the previous loop, since exceptions
            # might set a previously established kerning pair to be 0.
            cleanKerningPairs = dict(kerningPairs)
            for pair in kerningPairs:
                if kerningPairs[pair] == 0:
                    del cleanKerningPairs[pair]
            return cleanKerningPairs

        else:
            return kerningPairs


def get_args(args=None):

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    def check_suffix(file_name):
        fn = Path(file_name)
        if fn.suffix.lower() != '.ufo':
            parser.error(f'{fn.name} is not a UFO file')
        return file_name

    parser.add_argument(
        'ufo_file',
        type=lambda f: check_suffix(f),
        metavar='UFO',
        help='UFO file',
    )
    return parser.parse_args(args)


def run(font, print_list=False):
    ukr = UFOkernReader(font, includeZero=True)
    output = '\n'.join(ukr.output)

    if print_list:
        print(output + '\n')

    print('Total amount of kerning pairs:', len(ukr.output))


if __name__ == '__main__':
    try:
        # inRF
        import mojo
        f = CurrentFont()
        if f:
            run(f)
        else:
            print('You need to open a font first. 😥')

    except ImportError:
        from defcon import Font
        args = get_args()
        ufo = args.ufo_file
        f = Font(ufo)
        run(f, print_list=True)
