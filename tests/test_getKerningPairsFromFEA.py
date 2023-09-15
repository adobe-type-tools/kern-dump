import sys
from pathlib import Path

if '..' not in sys.path:
    sys.path.append('..')  # https://stackoverflow.com/a/16985066

import getKerningPairsFromFEA as gkp

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
    args = gkp.get_args(['dummy.fea'])  # args through argparse
    assert(args.feature_file == 'dummy.fea')
    assert(args.goadb_file is None)

    args = gkp.get_args(['dummy.fea', 'my_godadb'])
    assert(args.feature_file == 'dummy.fea')
    assert(args.goadb_file == 'my_godadb')


def test_group_group():
    input_file = TEST_DIR / 'group_group_test.fea'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.FEAKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))
    assert len(kfr.output) == 5 * 5


def test_ad_hoc_groups():
    input_file = TEST_DIR / 'ad_hoc_group_test.fea'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.FEAKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))
    assert len(kfr.output) == 53


def test_enum():
    input_file = TEST_DIR / 'enum_test.fea'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.FEAKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))
    assert len(kfr.output) == 52


def test_nested_groups():
    input_file = TEST_DIR / 'nested_group_test.fea'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.FEAKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))
    assert len(kfr.output) == 32


def test_rtl():
    input_file = TEST_DIR / 'rtl_test.fea'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.FEAKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))


def test_goadb():
    input_file = TEST_DIR / 'goadb_test.fea'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.FEAKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))
    goadb_file = TEST_DIR / 'goadb'
    dump_file = REFERENCE_DIR / 'goadb_test_converted.kerndump'
    kfr = gkp.FEAKernReader(input_file, goadb_file=goadb_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))


def test_catchall():
    input_file = TEST_DIR / 'catchall_test.fea'
    dump_file = REFERENCE_DIR / input_file.with_suffix('.kerndump').name
    kfr = gkp.FEAKernReader(input_file)
    assert('\n'.join(kfr.output) == read_file(dump_file))
