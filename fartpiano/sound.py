from sounddevice import OutputStream, CallbackFlags 
from threading   import Thread
from numpy       import ndarray
from typing      import Any
from time        import sleep

from .sample import Sample, Bank
from .pitch  import Pitch


class SoundAction(Thread):
    def __init__(self, sample: Sample) -> None:
        Thread.__init__(self)
        self._sample = sample
        self._playing = False
        self._attack_playing = False
        self._sustain_playing = False
        self._decay_playing = False
        self._release = False
        self._current_index = 0

    def attack(self) -> None:
        if not self._playing:
            self.start()

    def audio_callback(self, outdata: ndarray, frames: int, time: Any, status: CallbackFlags) -> None:
        print(f'Need {frames} frames')
        print(f'Attack {len(self._sample.attack_sample[0])} frames')
        print(f'Sustain {len(self._sample.sustain_sample[0])} frames')
        print(f'Decay {len(self._sample.decay_sample[0])} frames')

        frames_remaining = frames
        buffer_start = 0

        if self._attack_playing:
            start = self._current_index
            end = min(len(self._sample.attack_sample[0]), start + frames_remaining)
            outdata[buffer_start:buffer_start + end, 0] = self._sample.attack_sample[0][start:end]
            print(f'Pulling from attack sample [{start}:{end}] -> {end - start} frames')
            print(f'Buffer Fill [{buffer_start}:{buffer_start + end}]')
            if end - start < frames_remaining:
                frames_remaining =  frames_remaining - (end - start)
                self._attack_playing = False
                self._sustain_playing = True
                self._current_index = 0
                buffer_start = buffer_start + end

        if self._sustain_playing:
            while frames_remaining > 0 and not self._release:
                if self._current_index >= len(self._sample.sustain_sample[0]):
                    self._current_index = 0
                start = self._current_index
                end = min(len(self._sample.sustain_sample[0]), start + frames_remaining)
                outdata[buffer_start:buffer_start + (end - start), 0] = self._sample.sustain_sample[0][start:end]
                frames_remaining =  frames_remaining - (end - start)
                print(f'Pulling from sustain sample [{start}:{end}] -> {end - start} frames')
                print(f'Buffer Fill [{buffer_start}:{buffer_start + (end - start)}]')
                print(f'{frames_remaining} frames remaining')
                self._current_index = end
                buffer_start = buffer_start + (end - start)

        if self._decay_playing:
            while frames_remaining > 0:
                if self._current_index >= len(self._sample.decay_sample[0]):
                    self._playing = False  
                    outdata.fill(0)
                else:
                    start = self._current_index
                    end = min(len(self._sample.decay_sample[0]), start + frames_remaining)
                    outdata[buffer_start:buffer_start + (end - start), 0] = self._sample.decay_sample[0][start:end]
                    frames_remaining = frames_remaining - (end - start)
                    print(f'Pulling from decay sample [{start}:{end}] -> {end - start} frames')
                    print(f'Buffer Fill [{buffer_start}:{buffer_start + (end - start)}]')
                    print(f'{frames_remaining} frames remaining')
                    self._current_index = end
                    buffer_start = buffer_start + (end - start)
                
    def run(self) -> None:
        self._playing = True
        self._attack_playing = True
        self._sustain_playing = False
        self._decay_playing = False
        self._current_index = 0 

        # Set up the output stream
        with OutputStream(callback=self.audio_callback, channels=1, samplerate=self._sample.attack_sample[1], blocksize=512) as stream:
            while self._playing:
                sleep(1)

    def release(self) -> None:
        self._release = True
        self._decay_playing = True
        self._current_index = 0


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
            self._actions[pitch].join()
            del self._actions[pitch]

    def stop_all(self):
        for pitch in list(self._actions.keys()):
            self.release(pitch)
    
    