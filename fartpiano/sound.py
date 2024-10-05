from sounddevice import play, wait as sd_wait
from threading   import Thread
from numpy       import ndarray
from typing      import Tuple

from .sample import Sample, Bank
from .pitch  import Pitch


class SoundAction(Thread):
    def __init__(self, sample: Sample) -> None:
        Thread.__init__(self)
        self._sample = sample
        self._playing = False

    def attack(self) -> None:
        if not self._playing:
            self.start() 

    def do_play(self, sample: Tuple[ndarray, float]) -> None:
        play(data=sample[0], samplerate=sample[1])
        sd_wait()

    def run(self) -> None:
        self._playing = True
        self.do_play(self._sample.attack_sample)
        while self._playing:
            self.do_play(self._sample.sustain_sample)
        self.do_play(self._sample.decay_sample)
            
    def release(self) -> None:
        self._playing = False


class SoundManager(object):
    def __init__(self, bank: Bank) -> None:
        self._bank = bank
        self._actions = {}

    def attack(self, pitch: Pitch) -> None:
        print(f'Playing {pitch}')
        if pitch not in self._actions:
            sa = SoundAction(self._bank.samples[pitch])
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
    
    