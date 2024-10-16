from argparse import ArgumentParser

from .midi    import MIDIDeviceManager
from .sampler import install_bank, get_bank, read_banks
from .utils   import get_configuration, get_default_bank_path
from .piano   import Piano



if __name__ == "__main__":
    parser = ArgumentParser(prog='FartSampler', description='TODO')
    args = parser.parse_args()

    midi_device_name = get_configuration().get('devices', 'midi') 
    device_manager = MIDIDeviceManager(midi_device_name)

    default_bank_dir = get_default_bank_path()
    read_banks(default_bank_dir)

    single_loop = get_configuration().getboolean('piano', 'single_loop', fallback=False)
    piano = Piano(get_bank(), single_loop)
    device_manager.add_listener(piano)

    device_manager.run()
    device_manager.join()
    