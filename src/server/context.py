import logging
import os
import yaml
from itertools import starmap

_CONFIG_FILE = 'config/config.yml'

_LOG_FORMAT = '%(levelname)s [%(asctime)s]: %(message)s'
_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
_AVAILABLE_LOG_LEVELS = [
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
    logging.NOTSET
]


class Context:
    """
    Singleton class to setup the configs for the server
    Configs priorities are as follows: Environment variables, Config files
    meaning an environment variable has precedence over the same variable
    in a config file
    """

    class __Config:

        def __init__(self):

            self.__environment = {
                k.lower(): v for (k, v) in os.environ.items()
            }

            with open(_CONFIG_FILE, 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)

            environment = starmap(lambda k, v: (k.lower(), v), config['environment'].items())
            for key, value in environment:
                if key not in self.__environment:
                    self.__environment[key] = value
            self.__config = config['server_variables']

        def __getattr__(self, name: str):
            if name in self.__environment:
                return self.__environment[name]
            if name in self.__config:
                return self.__config[name]
            logging.warning(f'''context variable not found: \'{name}\'''')
            return None

    __instance = __Config()

    def __new__(cls):
        cls.__setup_log_level()
        return Context.__instance

    @staticmethod
    def __setup_log_level():
        context_level = Context.__instance.log_level
        level = logging.INFO
        found = False
        for log_level in _AVAILABLE_LOG_LEVELS:
            if context_level == logging.getLevelName(log_level):
                level = log_level
                found = True
                break
        logging.basicConfig(level=level,
                            format=_LOG_FORMAT,
                            datefmt=_LOG_DATE_FORMAT)
        if not found:
            logging.info('Log level invalid or not specified. Defaults to INFO.')
