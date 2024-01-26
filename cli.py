import logging
import argparse

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def parse_arguments():
	parser = argparse.ArgumentParser(description='Process taskmaster options.')
	parser.add_argument('-c', dest='configuration_file_path', type=str, required=True,
						help='Specify the path of the configuration file.')
	args = parser.parse_args()
	return args
