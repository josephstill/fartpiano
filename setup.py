from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name='FartPiano',
    version='0.0',
    description='A midi event processor that makes fart sounds.', 
    author='Joseph',   
    license='GNU General Public License v3.0',    
    long_description=open('README.md').read(),        
    long_description_content_type='text/markdown',
    url='https://github.com/josephstill/fartpiano',  
    project_urls={                                 
        "Documentation": "https://github.com/username/project_name/wiki",
        "Source Code": "https://github.com/josephstill/fartpiano/blob/main/README.md",
        "Bug Tracker": "https://github.com/josephstill/fartpiano/issues",
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Sound',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='MIDI, audio, fart piano, sound effects, musical instrument, fun, playful, Python, sound synthesis, music technology',
    packages=find_packages(),
    include_package_data=True, 
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
    install_requires=parse_requirements('requirements.txt'),
)