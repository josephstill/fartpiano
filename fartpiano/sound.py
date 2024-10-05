from   sounddevice import play, wait as sd_wait
from   threading   import Thread

from .sample import Sample, Bank
from .pitch  import Pitch


class SoundAction(Thread):
    def __init__(self, sample: Sample) -> None:
        self._sample = sample
        self._playing = False

    def attack(self) -> None:
        if not self._playing:
            self.start() 

    def run(self) -> None:
        self._playing = True
        play(self._sample.attack_sample)
        sd_wait()
        while self._playing:
            play(self._sample.sustain_sample)
            sd_wait()
        play(self._sample.decay_sample)
        sd_wait()
            
    def release(self) -> None:
        self._playing = False


class SoundManager(object):
    def __init__(self, bank: Bank) -> None:
        self._bank = bank
        self._actions = {}

    def attack(self, pitch: Pitch) -> None:
        if pitch not in self._actions:
            sa = SoundAction(self._bank[pitch])
            self._actions[pitch] = sa
            sa.attack()

    def release(self, pitch: Pitch) -> None:
        if pitch in self._actions:
            self._actions[pitch].release()
            self._actions[pitch].join()
            del self._actions[pitch]

    def stop_all(self):
        for pitch in list(self._actions.keys()):
            self.release(pitch)
    
    