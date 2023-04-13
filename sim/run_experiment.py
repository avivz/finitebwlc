from typing import List

import argparse
import logging
import sys
import json

from .configuration import RunConfig, DownloadRules
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

    parser.add_argument("--" + RunConfig.VERBOSE,
                        action='store_true', help="print events to stdout")

    parser.add_argument('--' + RunConfig.PLOT, nargs=2, type=float, metavar=('START', 'END'),
                        help="plot a block diagram from <START> to <END> times")

    parser.add_argument('--' + RunConfig.INDUCE_SPLIT, nargs=2, type=float, metavar=('START', 'END'),
                        help="split the network from <START> to <END> times")

    parser.add_argument("--" + RunConfig.MODE, choices=[
                        'pos', 'pow'], help="which mode of operation we are using (currently ineffective, always use pow!)", required=True)

    parser.add_argument("--" + RunConfig.POS_ROUND_LENGTH, metavar="SECs",
                        help="How long the mining round is in PoS (valid only in PoS mode, defaults to 1sec)",
                        type=float, default=1)

    parser.add_argument("--" + RunConfig.DUMB_ATTACKER, metavar="MINING_POWER",
                        help="include an attacker with the given mining power (defaults to no attacker)",
                        type=float, default=0)

    parser.add_argument("--" + RunConfig.TEASING_ATTACKER, metavar="MINING_POWER", type=float,
                        help="include a teasing attacker with the given mining power (defaults to no attacker)",
                        default=0)

    parser.add_argument("--" + RunConfig.EQUIVOCATION_TEASING_ATTACKER, metavar="MINING_POWER", type=float,
                        help="include a equivocating teasing attacker with the given mining power (defaults to no attacker)",
                        default=0)

    parser.add_argument("--" + RunConfig.ATTACKER_HEAD_START, metavar="NUM_BLOCKS", type=int,
                        help="give any attacker NUM_BLOCKS mining at the begining of the simulation. This only matters if an attacker is present.",
                        default=0)

    parser.add_argument("--" + RunConfig.RUN_TIME, default=100, required=True, type=float,
                        help="time to run")

    parser.add_argument("--" + RunConfig.DOWNLOAD_RULE, default=DownloadRules.LongestHeaderChain.value, choices=[rule.value for rule in DownloadRules], required=False, type=str,
                        help="The download rule to use")

    parser.add_argument("--" + RunConfig.NUM_HONEST, default=10, required=True, type=int,
                        help="number of honest nodes")

    parser.add_argument("--" + RunConfig.HONEST_BLOCK_RATE, default=0.1, required=True, type=float,
                        help="mining power of each honest node")

    parser.add_argument("--" + RunConfig.BANDWIDTH, default=1, required=True, type=float,
                        help="bandwidth of each honest node")

    parser.add_argument("--" + RunConfig.HEADER_DELAY, default=0, required=True, type=float,
                        help="header_delay header delay of each honest node")

    parser.add_argument('--' + RunConfig.SAVE_RESULTS, default="", type=str,
                        help="filename (Where to save the results of the simulation)")
    return parser


if __name__ == "__main__":
    parser = setup_parser()
    run_cfg = RunConfig()
    parser.parse_args(namespace=run_cfg)

    if run_cfg.verbose:
        logger = logging.getLogger("SIM_INFO")
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    experiment = Experiment(run_cfg)
    experiment.run_experiment()

    result = experiment.get_results()

    # write the results to stdout or file:
    if run_cfg.save_results:
        file_name = run_cfg.save_results
        with open(file_name, 'w') as out_file:
            json.dump(result, out_file, indent=2)
    else:
        json.dump(result, sys.stdout, indent=2)
