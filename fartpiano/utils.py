from configparser import ConfigParser
from importlib    import resources as pkg_resources
from pathlib      import Path

config: ConfigParser = None

def get_configuration() -> ConfigParser:
    global config
    if not config:
        config_file = get_configuration_file()
        config = ConfigParser()
        config.read_string(config_file.read_text())
    return config

def get_configuration_file() -> Path:
    user_config = Path.home()/'.fartpiano'/'piano.ini'
    run_in_source = Path.cwd()/'resources'/'configuration'/'piano.ini'

    if user_config.exists():
        return user_config
    elif pkg_resources.is_resource('fartpiano.resources.configuration', 'piano.ini'):
        with pkg_resources.path('fartpiano.resources.configuration', 'piano.ini') as packaged:
            return packaged
    else:
        return run_in_source    
