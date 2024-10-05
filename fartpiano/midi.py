from enum      import Enum
from abc       import ABC, abstractmethod
from typing    import List
from threading import Thread
from mido      import open_input

from .pitch import Pitch 

class MIDIEventType(Enum):
    PRESS   = 0
    RELEASE = 1

class MIDIEvent(object):

    def __init__(self, event: MIDIEventType, note: str, velocity: float) -> None:
        self._event = event
        self._note = Pitch.from_midi(note)
        self._velocity = velocity

    def __str__(self) -> str:
        return f'{self._event.name} {self._note}'

    @property
    def event(self) -> MIDIEventType:
        return self._event
    
    @property
    def note(self) -> Pitch:
        return self._note
    
    @property
    def velocity(self) -> float:
        return self._velocity
    
class MIDIEventListener(ABC):
    
    @abstractmethod
    def on_midi_event(self, event: MIDIEvent) -> None:
        raise NotImplementedError(f'{type(self).__name__} does not implement on_midi_event')

class MIDIDeviceManager(Thread):

    def __init__(self, device_id: str) -> None:
        Thread.__init__(self)
        self._device_id = device_id
        self._listeners: List[MIDIEventListener] = []
        self._running = False

    def add_listener(self, listtener: MIDIEventListener) -> None:
        self._listeners.append(listtener)

    def run(self) -> None:
        self._running = True
        with open_input(self._device_id) as midi_in:
            while self._running:
                for msg in midi_in.iter_pending():
                    if msg.type == 'note_on':
                        event = MIDIEvent(MIDIEventType.PRESS, msg.note, msg.velocity)
                    elif msg.type == 'note_off':
                        event = MIDIEvent(MIDIEventType.RELEASE, msg.note, msg.velocity)
                    else:
                        continue
                    self._notify_listeners(event)

    def _notify_listeners(self, event: MIDIEvent) -> None:
        for listener in self._listeners:
            listener.on_midi_event(event)

    def stop(self) -> None:
        self._running = False

