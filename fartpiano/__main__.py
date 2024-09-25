from pathlib  import Path
from argparse import ArgumentParser

from .sampler import create_bank


if __name__ == "__main__":
    parser = ArgumentParser(prog='FartSampler', description='TODO')
    parser.add_argument('-i', '--input-file', default=None, type=Path, help='The path of the input file to sample')
    args = parser.parse_args()

    if not args.input_file:
        print('Please supply a file for sampling')
        exit(-1)
    
    create_bank(args.input_file)

    