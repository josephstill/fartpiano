from .midi    import MIDIEventListener, MIDIEvent, MIDIEventType
from .sampler import Bank
from .sound   import SoundManager

class Piano(MIDIEventListener):

    def __init__(self, bank: Bank) -> None:
        self._sound_manager = SoundManager(bank)

    def on_midi_event(self, event: MIDIEvent) -> None:
        print(event)
        if event.event == MIDIEventType.PRESS:
            self._sound_manager.attack(event.note)
        elif event.event == MIDIEventType.RELEASE: 
            self._sound_manager.release(event.note)



