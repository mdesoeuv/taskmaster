import logging
import argparse

logger = logging.getLogger("taskmaster: " + __name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def parse_arguments():
	parser = argparse.ArgumentParser(description='Process taskmaster options.')
	parser.add_argument('integers', metavar='N', type=int, nargs='+',
						help='an integer for the accumulator')
	parser.add_argument('--sum', dest='accumulate', action='store_const',
						const=sum, default=max,
						help='sum the integers (default: find the max)')

	args = parser.parse_args()
	print(args.accumulate(args.integers))