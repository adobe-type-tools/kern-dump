import sys
from pathlib import Path

if '..' not in sys.path:
    sys.path.append('..')  # https://stackoverflow.com/a/16985066

import getKerningPairsFromOTF as gkp

TEST_DIR = Path(__file__).parent
REFERENCE_DIR = TEST_DIR / 'kerndumps_expected'


def read_file(path):
    '''
    Read a file, return the data
    '''

    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data


def test_get_args():
    args = gkp.get_args(['dummy.otf'])
    assert(args.font_file == 'dummy.otf')
    args = gkp.get_args(['dummy.ttf'])
    assert(args.font_file == 'dummy.ttf')


def test_catchall():
    input_file = TEST_DIR / 'roundtrip' / 'otf_kern_example.otf'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.OTFKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))
