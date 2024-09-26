from pathlib  import Path
from argparse import ArgumentParser

from .midi   import MIDIDeviceManager
from sampler import install_bank, get_bank, read_banks




from .sampler import create_bank


if __name__ == "__main__":
    parser = ArgumentParser(prog='FartSampler', description='TODO')
    parser.add_argument('-i', '--input-file', default=None, type=Path, help='The path of the input file to sample')
    args = parser.parse_args()

    midi_device_name = 'LPK25 mk2 0'
    device_manager = MIDIDeviceManager(midi_device_name)
    device_manager.run()

    device_manager.join()
    