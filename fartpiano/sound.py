from pygame.mixer import Sound, get_busy, pre_init, init as mixer_init
from threading    import Thread
from numpy        import ndarray
from typing       import Any
from time         import sleep

from .sample import Sample, Bank
from .pitch  import Pitch

class SoundAction(Thread):
    def __init__(self, sample: Sample) -> None:
        Thread.__init__(self)
        self._sample = sample
        self._attack_sample = Sound(sample.attack)
        self._sustain_sample = Sound(sample.sustain)
        self._decay_sample = Sound(sample.decay)
        self._sustain_length = self._sustain_sample.get_length()
        self._playing = False
        self._release = False

    def attack(self) -> None:
        if not self._playing:
            self.start()

    def run(self) -> None:
        self._playing = True
        self._release = False

        attack_channel = self._attack_sample.play()
        while attack_channel.get_busy():
            sleep(0.001)

        sustain_channel = self._sustain_sample.play(loops=-1)
        while not self._release:
            sleep(0.1)
        self._sustain_sample.stop()
        while sustain_channel.get_busy():
            sleep(0.001)        

        decay_channel = self._decay_sample.play()
        while decay_channel.get_busy():
            sleep(0.001)
        self._playing = False

    def release(self) -> None:
        self._release = True


class SoundManager(object):
    def __init__(self, bank: Bank) -> None:
        self._bank = bank
        self._actions = {}

    def attack(self, pitch: Pitch) -> None:
        if pitch not in self._actions:
            sa = SoundAction(self._bank.samples[pitch])
            self._actions[pitch] = sa
            sa.attack()

    def release(self, pitch: Pitch) -> None:
        if pitch in self._actions:
            self._actions[pitch].release()
            # self._actions[pitch].join()
            del self._actions[pitch]

    def stop_all(self):
        for pitch in list(self._actions.keys()):
            self.release(pitch)

def init_sound() -> None:
    pre_init(44100, -16, 1, 512)
    mixer_init()
    
    