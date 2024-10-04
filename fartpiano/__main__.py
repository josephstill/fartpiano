from pathlib  import Path
from argparse import ArgumentParser

from .midi    import MIDIDeviceManager, MIDIEventListener, MIDIEvent
from .sampler import install_bank, get_bank, read_banks
from .utils   import get_configuration

class TestMidiEvents(MIDIEventListener):
    def on_midi_event(self, event: MIDIEvent) -> None:
        print(event)


if __name__ == "__main__":
    parser = ArgumentParser(prog='FartSampler', description='TODO')
    args = parser.parse_args()

    midi_device_name = get_configuration()['devices']['midi'].replace('"', '')
    device_manager = MIDIDeviceManager(midi_device_name)
    test_listener = TestMidiEvents()
    device_manager.add_listener(test_listener)
    device_manager.run()

    device_manager.join()
    