from librosa         import load as rosa_load, piptrack
from librosa.feature import rms as rms_calculation
from numpy           import arange, max as np_max, where as np_where, argmax, ndarray
from pathlib         import Path
from soundfile       import write as sf_write
from typing          import Tuple, Dict, Any
from .pitch          import Pitch

class Sample(object):

    def __init__(self, attack: Path, sustain: Path, decay: Path, pitch: Pitch) -> None:
        self._attack = attack
        self._sustain = sustain
        self._decay = decay
        self._pitch = pitch
        self._attack_sample = None
        self._sustain_sample = None
        self._decay_sample = None

    def __str__(self) -> str:
        return f'Sample:\n\tAttack:  {self.attack}\n\tSustain: {self.sustain}\n\tDecay:  {self.decay}\n\tPitch:  {self.pitch}'

    @property
    def attack(self) -> Path:
        return self._attack
    
    @property
    def sustain(self) -> Path:
        return self._sustain
    
    @property
    def decay(self) -> Path:
        return self._decay
    
    @property
    def attack_sample(self) -> Tuple[ndarray, float]:
        return self._attack_sample
    
    @property
    def sustain_sample(self) -> Tuple[ndarray, float]:
        return self._sustain_sample
    
    @property
    def decay_sample(self) -> Tuple[ndarray, float]:
        return self._decay_sample
    
    @property
    def pitch(self) -> Pitch:
        return self._pitch
    
    def load(self, sample_root: Path) -> None:
        attack_load = sample_root/self.attack.name
        sustain_load = sample_root/self.sustain.name
        decay_load = sample_root/self.decay.name
        self._attack_sample = rosa_load(attack_load, sr=None)
        self._sustain_sample = rosa_load(sustain_load, sr=None)
        self._decay_sample = rosa_load(decay_load, sr=None)

    def to_dict(self) -> Dict[str, str]:
        return {
            "pitch": str(self.pitch),
            "attack": self.attack.name,
            "sustain": self.sustain.name,
            "decay": self.decay.name
        }
    
    @classmethod
    def from_dict(cls, dict: Dict[str, str]) -> 'Sample':
        attack = Path(dict['attack'])
        sustain = Path(dict['sustain'])
        decay = Path(dict['decay'])
        pitch = Pitch.from_string(dict['pitch'])

        if not pitch:
            return None
        
        return Sample(attack, sustain, decay, pitch)
    
class Bank(object):

    def __init__(self, name: str) -> None:
        self._name = name
        self._samples: Dict[Pitch, Sample] = {}

    def __str__(self) -> str:
        return f'Sample Bank: {self._name}'

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def samples(self) -> Dict[Pitch, Sample]:
        return self._samples

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'samples': [self.samples[pitch].to_dict() for pitch in self.samples]
        }
    
    def add_sample(self, pitch: Pitch, sample: Sample) -> None:
        self._samples[pitch] = sample

    def load(self, sample_intall_path: Path) -> None:
        sample_root = sample_intall_path/self.name
        if sample_root.exists():
            for sample_pitch in self.samples:
                self.samples[sample_pitch].load(sample_root)
    
    @classmethod
    def from_dict(cls, dict: Dict[str, Any]) -> 'Bank':
        ret = Bank(dict['name'])
        for sample in dict['samples']:
            new_sample = Sample.from_dict(sample)
            if not new_sample:
                return None
            ret.add_sample(new_sample.pitch, new_sample)
        return ret
        
def define_boundries(file_path: Path, frame_length=2048, hop_length=512, attack_percent=.75, sustain_percent=0.5) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    # Load the samples
    y, sr = rosa_load(file_path, sr=None)
    
    # Calculate the intensity of the samples
    rms = rms_calculation(y=y, frame_length=frame_length, hop_length=hop_length).flatten()

    max_rms = np_max(rms)
    attack_threshold = attack_percent * max_rms
    sustain_threshold = sustain_percent * max_rms

    attack_start = 0
    attack_end = int(argmax(rms > attack_threshold))
    sustain_start = attack_end + 1
    sustain_end = int(sustain_start + argmax(rms[sustain_start:] < sustain_threshold))
    decay_start = sustain_end + 1
    decay_end = int(decay_start + argmax(rms[decay_start:] == 0))

    ret = ((attack_start, attack_end * hop_length), (attack_end * hop_length, sustain_end * hop_length ), (sustain_end * hop_length, decay_end * hop_length))
    return ret

def create_sample(file_path: Path, pitch: Pitch, boundries: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]) -> Sample:
    
    y, sr = rosa_load(file_path, sr=None)
    
    # Grab the sample buffers
    attack_segment = y[boundries[0][0]:boundries[0][1]]
    sustain_segment = y[boundries[1][0]:boundries[1][1]]
    decay_segment = y[boundries[2][0]:boundries[2][1]]


    attack_file = file_path.with_name(file_path.stem + '_attack.wav')
    sustain_file = file_path.with_name(file_path.stem + '_sustain.wav')
    decay_file = file_path.with_name(file_path.stem + '_decay.wav')

    sf_write(attack_file, attack_segment, sr)
    sf_write(sustain_file, sustain_segment, sr)
    sf_write(decay_file, decay_segment, sr)

    sample = Sample(attack_file, sustain_file, decay_file, pitch)
    return sample
