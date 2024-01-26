import logging
import argparse
import yaml
import pathlib
from exceptions import ConfigError 
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

def config_file_parser(path: pathlib.Path):
    if not path.exists() or path.is_dir():
        raise ConfigError("The configuration `" + str(path) + "` file does not exist or is a directory.")
    with open(path) as file:
        config = yaml.load(file, Loader=Loader)
        logger.info("Configuration file parsed successfully.")
        logger.info(config)

def parse_arguments():
	parser = argparse.ArgumentParser(description='Process taskmaster options.')
	parser.add_argument('-c', dest='configuration_file_path', type=str, required=True,
						help='Specify the path of the configuration file.')
	args = parser.parse_args()
	return args

def parse_args_and_config():
	logger.info("Hello !")
	args = parse_arguments()
	config_file_parser(pathlib.Path(args.configuration_file_path))
