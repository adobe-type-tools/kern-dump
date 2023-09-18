import sys
from pathlib import Path

if '..' not in sys.path:
    sys.path.append('..')  # https://stackoverflow.com/a/16985066

import dumpkerning as dk
import dumpKernFeatureFromOTF

TEST_DIR = Path(__file__).parent
ROUNDTRIP_DIR = TEST_DIR / 'roundtrip'


def read_file(path):
    '''
    Read a file, return the data
    '''

    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data


def test_get_args():
    file_list = ['dummy.fea', 'dummy.otf', 'dummy.fea']
    args = dk.get_args(file_list)
    assert(args.sourceFiles == file_list)
    assert(args.outputDir is None)

    args = dk.get_args(['dummy_file', '--output', 'dummy_dir'])
    assert(args.sourceFiles == ['dummy_file'])
    assert(args.outputDir == 'dummy_dir')


def test_equality():
    input_fea = ROUNDTRIP_DIR / 'fea_kern_example.fea'
    input_otf = ROUNDTRIP_DIR / 'otf_kern_example.otf'
    input_ufo = ROUNDTRIP_DIR / 'ufo_kern_example.ufo'

    fea_dump = dk.extractKerning(input_fea)
    otf_dump = dk.extractKerning(input_otf)
    ufo_dump = dk.extractKerning(input_ufo)

    # compare the dict data
    assert(fea_dump == otf_dump)
    assert(otf_dump == ufo_dump)
    assert(ufo_dump == fea_dump)

    fea_dump_file = input_fea.with_suffix('.dumped')
    otf_dump_file = input_otf.with_suffix('.dumped')
    ufo_dump_file = input_ufo.with_suffix('.dumped')

    dk.dumpKerning(fea_dump, fea_dump_file)
    dk.dumpKerning(otf_dump, otf_dump_file)
    dk.dumpKerning(ufo_dump, ufo_dump_file)

    # compare the actual dumps
    assert(read_file(fea_dump_file) == read_file(otf_dump_file))
    assert(read_file(otf_dump_file) == read_file(ufo_dump_file))
    assert(read_file(ufo_dump_file) == read_file(fea_dump_file))
    fea_dump_file.unlink()
    otf_dump_file.unlink()
    ufo_dump_file.unlink()


def test_roundtrip():
    input_otf = ROUNDTRIP_DIR / 'otf_kern_example.otf'
    dump_file = input_otf.with_suffix('.dumped')
    fea_data = dumpKernFeatureFromOTF.makeKernFeature(input_otf)
    with open(dump_file, 'w') as blob:
        blob.write('\n'.join(fea_data))
    fea_dump = dk.extractKerning(dump_file)
    otf_dump = dk.extractKerning(input_otf)
    assert(fea_dump == otf_dump)
    dump_file.unlink()


def test_main():
    input_otf = ROUNDTRIP_DIR / 'otf_kern_example.otf'
    output_dir = TEST_DIR / 'temp_dir'
    dk.main(args=[str(input_otf), '--output', str(output_dir)])
    new_suffix = input_otf.suffix + '.kerndump'
    new_dump = output_dir / input_otf.with_suffix(new_suffix).name
    # file with same name in different folder
    existing_dump = TEST_DIR / 'kerndumps_expected' / new_dump.name
    assert(read_file(new_dump) == read_file(existing_dump))
    new_dump.unlink()
    output_dir.rmdir()
