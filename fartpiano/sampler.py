from pathlib import Path
from typing  import Dict
from json    import dumps
from zipfile import ZipFile

from .sample import define_boundries, Sample, create_sample, Bank
from .pitch  import Pitch, Note, correct_pitch, pitch_shift_sample

def create_bank(input_file: Path) -> None:
    
    # define the boundries from the input file
    boundries = define_boundries(input_file)

    files: Dict[Pitch, Path] = {}
    bank = Bank(input_file.stem)

    # Pitch correct the input file
    corrected_file, corrected_pitch = correct_pitch(input_file)
    files[corrected_pitch] = corrected_file

    # Create a version for each pitch
    for pitch in Pitch.iterate():
        if pitch != corrected_pitch:
            adjusted_file, adjusted_pitch = pitch_shift_sample(corrected_file, corrected_pitch, pitch)
            files[adjusted_pitch] = adjusted_file

    # Create a sample bank
    for pitch in files:
        new_sample = create_sample(files[pitch], pitch, boundries)
        bank.add_sample(pitch, new_sample)
        files[pitch].unlink()

    # Create a bank discription
    bank_file = input_file.parent/f'{bank.name}.json'
    bank_file.write_text(dumps(bank.to_dict(), indent=4))


    # Zip up the bank for importing
    bank_zip = input_file.parent/f'{bank.name}.zip'
    with ZipFile(bank_zip, 'w') as zip_file:
        zip_file.write(bank_file, arcname=bank_file.name)
        for sample_pitch in bank.samples:
            sample = bank.samples[sample_pitch]
            zip_file.write(sample.attack, arcname=sample.attack.name)
            zip_file.write(sample.sustain, arcname=sample.sustain.name)
            zip_file.write(sample.decay, arcname=sample.decay.name)

    # Remove artifact files
    bank_file.unlink()
    for sample_pitch in bank.samples:
        sample = bank.samples[sample_pitch]
        sample.attack.unlink()
        sample.sustain.unlink()
        sample.decay.unlink()

    print(f'Sample bank created: {bank_zip}')



    



