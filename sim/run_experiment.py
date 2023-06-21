from typing import List

import argparse
import logging
import sys
import json

from .experiment import Experiment


class MyParser(argparse.ArgumentParser):
    @staticmethod
    def convert_arg_line_to_args(arg_line: str) -> List[str]:
        return arg_line.split()


def setup_parser() -> argparse.ArgumentParser:
    parser = MyParser(
        prog='run_experiment',
        description='Run a basic experiment of the mining simulation.\nSpecify a configuration file with @<filename>.',
        fromfile_prefix_chars='@')

    # TODO simplify:
    parser.add_argument('--verbose',
                        action='store_true', help="print events to stdout")

    parser.add_argument('--plot', nargs=2, type=float, metavar=('START', 'END'),
                        help="plot a block diagram from <START> to <END> times")

    parser.add_argument('--save_results', default="", type=str,
                        help="filename (Where to save the results of the simulation)")

    # add a parser argument to read the json config file
    parser.add_argument('--config_file', '-c', default="", type=str,
                        help="filename (Where to read the config file)", required=True)

    parser.add_argument('--log_blocks', default="", type=str,
                        help="filename (Where to save a log of the blocks created during the simulation)")
    return parser


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()

    # get the config file:
    with open(args.config_file) as config_file:
        config = json.load(config_file)

    if args.log_blocks:
        logger = logging.getLogger("BLOCK_LOG")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(args.log_blocks, mode='w')
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    if args.verbose:
        logger = logging.getLogger("SIM_INFO")
        logger.setLevel(logging.INFO)

        handler2 = logging.StreamHandler(sys.stdout)
        handler2.setLevel(logging.INFO)
        logger.addHandler(handler2)

    experiment = Experiment(config, args.plot)
    experiment.run_experiment()

    result = experiment.get_results()

    # write the results to stdout or file:
    if args.save_results:
        file_name = args.save_results
        with open(file_name, 'w') as out_file:
            json.dump(result, out_file, indent=2)
    else:
        json.dump(result, sys.stdout, indent=2)
