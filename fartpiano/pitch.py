from numpy           import median as np_median, mean as np_mean, array, arange, concatenate, float32, log2 as np_log2
from librosa         import load as rosa_load, piptrack
from librosa.effects import pitch_shift
from pathlib         import Path
from enum            import Enum
from math            import log2
from typing          import Tuple
from soundfile       import write as sf_write

class Note(Enum):
    C       = {'name': 'C',  'reference': 261.63}
    C_SHARP = {'name': 'C#', 'reference': 277.18}
    D       = {'name': 'D',  'reference': 293.66}
    D_SHARP = {'name': 'D#', 'reference': 311.13}
    E       = {'name': 'E',  'reference': 329.63}
    F       = {'name': 'F',  'reference': 349.23}
    F_SHARP = {'name': 'F#', 'reference': 369.99}
    G       = {'name': 'G',  'reference': 392.00}
    G_SHARP = {'name': 'G#', 'reference': 415.30}
    A       = {'name': 'A',  'reference': 440.00}
    A_SHARP = {'name': 'A#', 'reference': 466.16}
    B       = {'name': 'B',  'reference': 493.88}

    def __str__(self) -> str:
        return self.value['name']
    
    @property
    def note_name(self) -> str:
        return self.value['name']
    
    @property 
    def reference(self) -> float:
        return self.value['reference']
    
    def __gt__(self, other: 'Note') -> bool:
        notes = list(Note)  # Convert enum to list
        current_index = notes.index(self)
        other_index = notes.index(other)   
        return current_index > other_index
    
    def __lt__(self, other: 'Note') -> bool:
        notes = list(Note)  # Convert enum to list
        current_index = notes.index(self)
        other_index = notes.index(other)   
        return current_index < other_index
    
    def __ge__(self, other: 'Note') -> bool:
        return not self.__lt__(other)
    
    def __le__(self, other: 'Note') -> bool:
        return not self.__gt__(other)
    
    def __add__(self, step: int) -> 'Note':
        notes = list(Note)  # Convert enum to list
        current_index = notes.index(self)
        new_index = (current_index + step) % len(notes)  # Circular behavior using modulo
        return notes[new_index]

    def __radd__(self, step: int) -> 'Note':
        return self.__add__(step)

    def __sub__(self, step: int) -> 'Note':
        notes = list(Note)
        current_index = notes.index(self)
        new_index = (current_index - step) % len(notes)
        return notes[new_index]
    
    def __hash__(self) -> int:
        return hash(self.value['name'])
    
    @staticmethod
    def get_closest_note(frequency: float) -> 'Note':
        closest_note = None
        closest_diff = float('inf')

        # Iterate over each note in the enum
        for note in Note:
            ref_frequency = note.reference
            # Calculate the octave difference by finding the closest multiple of the reference frequency
            # that is near the given frequency.
            octave = round(log2(frequency / ref_frequency))
            scaled_frequency = ref_frequency * (2 ** octave)
            
            # Calculate the difference between the actual frequency and the scaled frequency
            difference = abs(frequency - scaled_frequency)

            # Find the closest note based on the smallest difference
            if difference < closest_diff:
                closest_diff = difference
                closest_note = note
        
        return closest_note
    
    @classmethod
    def from_string(cls, val: str) -> 'Note':
        for note in Note:
            if note.value['name'] == val:
                return note
        return None

_OCTAVE_ORDER = list(Note)  # Caching the list of Note values for better performance

class _PitchIterator:

    def __init__(self, start_pitch: 'Pitch', end_pitch: 'Pitch') -> None:
        self._current_pitch = start_pitch
        self._last_pitch = end_pitch

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_pitch > self._last_pitch:
            raise StopIteration
        next_pitch = self._current_pitch
        self._current_pitch = next_pitch + 1
        return next_pitch
    
class Pitch(object):
    
    def __init__(self, note: Note = Note.C, octave: int = 4) -> None:
        self._update_frequency(note, octave)

    def __str__(self) -> str:
        return f'{self._note}{self._octave}'
    
    def __gt__(self, other: 'Pitch') -> bool:
        return self.frequency > other.frequency
    
    def __lt__(self, other: 'Pitch') -> bool:
        return self.frequency < other.frequency
    
    def __ge__(self, other: 'Pitch') -> bool:
        return self.frequency >= other.frequency
    
    def __le__(self, other: 'Pitch') -> bool: 
        return self.frequency <= other.frequency
    
    def __eq__(self, other: 'Pitch') -> bool:
        return self.frequency == other.frequency
    
    def __ne__(self, other: 'Pitch') -> bool:
        return self.frequency != other.frequency
    
    def __hash__(self) -> int:
        return hash(self.frequency)

    @property
    def note(self) -> Note:
        return self._note
    
    @note.setter
    def note(self, note: Note) -> None:
        self._update_frequency(note, self.octave)

    @property
    def octave(self) -> int:
        return self._octave
    
    @octave.setter
    def octave(self, octave: int) -> None:
        self._update_frequency(self.note, octave)

    @property
    def frequency(self) -> float:
        return self._frequency
    
    @frequency.setter
    def frequency(self, frequency: float) -> None:
        # Calculate the number of semitones away from A4
        semitones_from_A4 = 12 * log2(frequency / Note.A.reference)

        # Round to nearest whole semitone
        nearest_semitone = round(semitones_from_A4)

        # Determine the note and octave from the semitone difference
        note_index = (nearest_semitone + 9) % 12  # A is at index 9
        octave = 4 + (nearest_semitone + 9) // 12

        # Assign the correct note
        note = _OCTAVE_ORDER[note_index]
        self._update_frequency(note, octave)


    def __add__(self, steps: int) -> 'Pitch':
        new_note_index = (_OCTAVE_ORDER.index(self._note) + steps) % len(_OCTAVE_ORDER)
        octave_adjustment = (_OCTAVE_ORDER.index(self._note) + steps) // len(_OCTAVE_ORDER)
        new_note = _OCTAVE_ORDER[new_note_index]
        new_octave = self._octave + octave_adjustment
        return Pitch(new_note, new_octave)

    def __sub__(self, steps: int) -> 'Pitch':
        new_note_index = (_OCTAVE_ORDER.index(self._note) - steps) % len(_OCTAVE_ORDER)
        octave_adjustment = (_OCTAVE_ORDER.index(self._note) - steps) // len(_OCTAVE_ORDER)
        new_note = _OCTAVE_ORDER[new_note_index]
        new_octave = self._octave + octave_adjustment
        return Pitch(new_note, new_octave)
    
    @classmethod
    def iterate(cls):
        return _PitchIterator(Pitch(Note.A, 2), Pitch(Note.C, 8))
    
    @classmethod
    def from_string(cls, val: str) -> 'Pitch':
        note = Note.from_string(val[:-1])
        try:  
            octave = int(val[-1])
        except ValueError:
            octave = None

        if not note or not octave:
            return None
        
        return Pitch(note, octave)

    @classmethod
    def from_midi(cls, val: str) -> 'Pitch':
        midi_note_number = int(val)
        note = _OCTAVE_ORDER[midi_note_number % 12]
        octave = (midi_note_number // 12) - 1
        return Pitch(note=note, octave=octave)
        
    def _update_frequency(self, note: Note, octave: int) -> None:
        self._note = note
        self._octave = octave

        # Calculate the semitone distance from A4
        note_index =  _OCTAVE_ORDER.index(note)
        semitone_difference = (octave - 4) * 12 + (note_index - 9)

        # Update the frequency using the formula for frequency
        self._frequency = Note.A.reference * (2 ** (semitone_difference / 12))

def analyze_dominant_pitch(file_path: Path, segment_duration: float = .1) -> Pitch:
    try:
        y, sr = rosa_load(file_path, sr=None)
        segment_samples = int(segment_duration * sr)
        
        pitches = []
        for start in range(0, len(y) - segment_samples, segment_samples):
            segment = y[start:start + segment_samples]
            pitches_segment, _ = piptrack(y=segment, sr=sr)
            
            # Flatten the pitch array and remove zero values
            pitches_segment = pitches_segment.flatten()
            pitches_segment = pitches_segment[pitches_segment > 0]
            
            if len(pitches_segment) > 0:
                mean_pitch = np_mean(pitches_segment)
                pitches.append(mean_pitch)
        
        if pitches:
            # Use median to find the most representative pitch
            dominant_pitch = np_median(pitches)        
            pitch = Pitch()
            pitch.frequency = dominant_pitch
            return pitch
        else:
            return None
    except Exception as e:
        return None
        
def correct_pitch(file_path: Path, segment_duration: float = .1) -> Tuple[Path, Pitch]:

    # detect the dominant pitch of the sound in the file
    dominant_pitch = analyze_dominant_pitch(file_path, segment_duration * 4)
    dominant_freq = dominant_pitch.frequency

    # Load the audio
    y, sr = rosa_load(file_path, sr=None)
           
    # Initialize an array for pitch-corrected audio
    corrected_audio = array([])
    
    # Iterate over the segments
    for start in arange(0, len(y) / sr, segment_duration):
        start_sample = int(start * sr)
        end_sample = int((start + segment_duration) * sr)
        segment_audio = y[start_sample:end_sample]
        
        # Detect pitch and apply pitch shift if necessary
        pitches, magnitudes = piptrack(y=segment_audio, sr=sr)
        pitches = pitches[pitches > 0]
        
        if len(pitches) > 0:
            mean_pitch = np_median(pitches)
            ratio = dominant_freq / mean_pitch
            shifted_audio = pitch_shift(y=segment_audio, sr=sr, n_steps=np_log2(ratio) * 12)
        else:
            shifted_audio = segment_audio
        
        # Append the pitch-corrected segment to the output
        corrected_audio = concatenate((corrected_audio, shifted_audio))
    
    # Save the corrected audio to a new file
    corrected_file_path = file_path.with_name(file_path.stem + f'_{dominant_pitch}.wav')
    sf_write(corrected_file_path, corrected_audio, sr)  # Use soundfile to write the audio
    
    return (corrected_file_path, dominant_pitch)

def pitch_shift_sample(file_path: Path, source: Pitch, dest: Pitch) -> Tuple[Path, Pitch]:

    dominant_freq = source.frequency
    dest_freq = dest.frequency
    ratio = dest_freq / dominant_freq
    n_steps = np_log2(ratio) * 12  # Calculate pitch shift in semitones

    # Load the audio from file
    y, sr = rosa_load(file_path, sr=None)

    # Apply pitch shift transformation
    shifted_audio = pitch_shift(y, sr=sr, n_steps=n_steps)

    sample_name = file_path.stem
    sample_name = sample_name.replace(str(source), str(dest))
    
    # Create the new file name based on the destination pitch
    shifted_file_path = file_path.with_stem(sample_name)

    # Save the pitch-shifted audio
    sf_write(shifted_file_path, shifted_audio, sr)

    return shifted_file_path, dest



