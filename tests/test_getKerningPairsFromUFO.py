import sys
from pathlib import Path
from defcon import Font
import pytest


if '..' not in sys.path:
    sys.path.append('..')  # https://stackoverflow.com/a/16985066

import getKerningPairsFromUFO as gkp

TEST_DIR = Path(__file__).parent
REFERENCE_DIR = TEST_DIR / 'kerndumps_expected'


def read_file(path):
    '''
    Read a file, return the data
    '''

    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data


def test_get_args(capsys):
    args = gkp.get_args(['dummy.ufo'])
    assert(args.ufo_file == 'dummy.ufo')
    args = gkp.get_args(['dummy.UFO'])
    assert(args.ufo_file == 'dummy.UFO')

    with pytest.raises(SystemExit):
        gkp.get_args(['dummy.ttf'])

    out, err = capsys.readouterr()
    assert 'dummy.ttf is not a UFO file' in err


def test_catchall():
    input_file = TEST_DIR / 'roundtrip' / 'ufo_kern_example.ufo'
    new_suffix = input_file.suffix + '.kerndump'
    dump_file = REFERENCE_DIR / input_file.with_suffix(new_suffix).name
    kfr = gkp.UFOkernReader(Font(input_file))
    assert('\n'.join(kfr.output) == read_file(dump_file))


def test_run(capsys):
    input_file = TEST_DIR / 'roundtrip' / 'ufo_kern_example.ufo'
    gkp.run(Font(input_file))
    out, err = capsys.readouterr()
    assert out == 'Total amount of kerning pairs: 134\n'
