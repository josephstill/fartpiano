from setuptools import setup, find_packages

setup(
    name='FartPiano',
    version='0.0',
    packages=find_packages(),
    include_package_data=True,  # Ensures resources are included
    package_data={
        'fartpiano': [
            'resources',
            'resources/banks',
            'resources/banks/fart/',
            'resources/banks/fart/*.wav',
            'resources/banks/fart/fart.json',
            'resources/configuration/piano.ini',
        ],
    },
    # Other setup arguments...
)