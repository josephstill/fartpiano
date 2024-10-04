from setuptools import setup, find_packages

setup(
    name='FartPiano',
    version='0.0',
    packages=find_packages(),
    include_package_data=True,  # Ensures resources are included
    package_data={
        'fartpiano': [
            'resources/banks/fart/fart.json',
            'resources/banks/fart/*.wav',
            'resources/configuration/piano.ini',
        ],
    },
    # Other setup arguments...
)