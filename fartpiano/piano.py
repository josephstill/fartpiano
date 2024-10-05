from .midi    import MIDIEventListener, MIDIEvent
from .sampler import Bank
from .sound   import SoundManager


class Piano(MIDIEventListener):

    def __init__(self, bank: Bank) -> None:
        self._sound_manager = SoundManager(bank)

    def on_midi_event(self, event: MIDIEvent) -> None:
        print(event)



