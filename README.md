# Fart Piano

## Description
This project is the controller for a fart piano. Its a more complecated version of a childrens toy. Currently the Fart Piano runs on Windows; however, its intended to run on Linux and will eventually be setup to run on a Raspberry Pi.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Configuration](#configuration)
- [Hardware](#hardware)
- [Notes](#notes)

## Installation
```bash
# Clone the repository
git clone git@github.com:josephstill/fartpiano.git

# Change to the project directory
cd fartpiano

# Build the package
python build.py
```

This will get a python wheel that you can install; however, its unnecessary as you can run the piano in the source tree. 

## Usage
After installing the wheel or changing directory into the source tree you can run the piano like so:
```bash
python -m fartpiano
```

## Configuration
Configuration is done by ini file. Here is a sample configuration file: 
```ini
[devices]
midi = LPK25 mk2 0

[piano]
single_loop = on
```

* devices; midi: Sets the name of the midi device that the piano searchs for input from
* piano; single_loop: Sets the piano in single loop mode where it doesn't attempt to loop samples while the keys are pressed.

Currently the piano works best in single loop mode. The piano searches for ``piano.ini`` in the users home directory in ``home/${USER}/.config/fartpiano/piano.ini``. If this file does not exist, the piano uses a default configuration packed with the application.

### Sample Banks
In theory, more sample banks can be added, though there aren't currently controls for changing banks. The piano will look for banks at ``home/${USER}/.cache/fartpiano/banks``. Banks are a collection of ``wav`` files and an associated ``json`` file to direct the piano as to which samples to load.

```json
{
    "name": "fart",
    "samples": [
        {
            "pitch": "G#5",
            "attack": "fart_G#5_attack.wav",
            "sustain": "fart_G#5_sustain.wav",
            "decay": "fart_G#5_decay.wav"
        },
        {
            "pitch": "A2",
            "attack": "fart_A2_attack.wav",
            "sustain": "fart_A2_sustain.wav",
            "decay": "fart_A2_decay.wav"
        }
    ]
}
```
This is a small exampe of the bank control file. It gives the name of the bank, and identifies the samples that will be played on attack (when the key is pressed), sustain (while the key is pressed), and decay (when the key is released). 

## Hardware
The goal is to support any keyboard that works with ``mido``; however, the piano has only been tested with the [AKAI LPK25](https://www.amazon.com/AKAI-Professional-LPK25-Controller-Arpeggiator/dp/B0BF9PCGM8/ref=asc_df_B0BF9PCGM8/?tag=hyprod-20&linkCode=df0&hvadid=693360658756&hvpos=&hvnetw=g&hvrand=5943621215822459942&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9011836&hvtargid=pla-1839585134330&mcid=3da40ab2f9103258b78fa35c2ddbcf1a&th=1)

## Notes
This is what happens when Dakota asks us to use his fart in a song. 
