from .midi    import MIDIEventListener, MIDIEvent, MIDIEventType
from .sampler import Bank
from .sound   import SoundManager, init_sound

class Piano(MIDIEventListener):

    def __init__(self, bank: Bank, single_loop_mode: bool = False) -> None:
        init_sound()
        self._sound_manager = SoundManager(bank, single_loop_mode)

    def on_midi_event(self, event: MIDIEvent) -> None:
        if event.event == MIDIEventType.PRESS:
            self._sound_manager.attack(event.note)
        elif event.event == MIDIEventType.RELEASE: 
            self._sound_manager.release(event.note)



