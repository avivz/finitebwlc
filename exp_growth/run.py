#!/usr/bin/python3
import numpy
import os
import argparse
from sim.configuration import RunConfig


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='run',
        description='Runs the experiment',
        fromfile_prefix_chars='@')

    parser.add_argument('--slurm',
                        action='store_true', help="runs the code in parallel on slurm using sbatch")  # on/off flag
    parser.add_argument('--no_out',
                        action='store_true', help="runs the code in parallel on slurm using sbatch")  # on/off flag
    return parser


BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
SIMULATION_MODULE = "sim.run_experiment"

PYTHON_PATH = "python"

OUTPUT_PATH = os.path.join(os.path.split(
    os.path.abspath(__file__))[0], "data/")

if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

base_arguments = [f"--{RunConfig.RUN_TIME} 10000", f"--{RunConfig.NUM_HONEST} 100", f"--{RunConfig.MODE} pow",
                  f"--{RunConfig.HONEST_BLOCK_RATE} 0.01"]

bandwidth_range = numpy.arange(0.05, 2.01, 0.05)
num_repetitions = 100

parser = setup_parser()
args = parser.parse_args()

num_skipped = 0
num_ran = 0

for index, bandwidth in enumerate(bandwidth_range):
    for rep in range(num_repetitions):
        file_name1 = os.path.join(
            OUTPUT_PATH, "exp1_band_" + str(index)+"_"+str(rep)+".json")
        arguments1 = base_arguments + \
            [f"--{RunConfig.HEADER_DELAY} 0 --{RunConfig.BANDWIDTH} {bandwidth}",
                f"--{RunConfig.SAVE_RESULTS} {file_name1}"]

        file_name2 = os.path.join(
            OUTPUT_PATH, "exp1_delay_" + str(index)+"_"+str(rep)+".json")
        arguments2 = base_arguments + \
            [f"--{RunConfig.HEADER_DELAY} {1/bandwidth} --{RunConfig.BANDWIDTH} -1",
                f"--{RunConfig.SAVE_RESULTS} {file_name2}"]

        cmd1 = f"{PYTHON_PATH} -m {SIMULATION_MODULE} {' '.join(arguments1)}"
        cmd2 = f"{PYTHON_PATH} -m {SIMULATION_MODULE} {' '.join(arguments2)}"

        if args.slurm:
            cmd1 = f'sbatch --mem=8g -c1 --wrap="{cmd1}"'
            cmd2 = f'sbatch --mem=8g -c1 --wrap="{cmd2}"'
            if args.no_out:
                cmd1 += ' --output=/dev/null'
                cmd2 += ' --output=/dev/null'

        if os.path.exists(file_name1) and os.path.getsize(file_name1) > 0:
            print(f"SKIPPING {file_name1}")
            num_skipped += 1
        else:
            print(f"{index}: RUNNING: {cmd1}")
            os.system(cmd1)
            num_ran += 1
        if os.path.exists(file_name2) and os.path.getsize(file_name2) > 0:
            print(f"SKIPPING {file_name2}")
            num_skipped += 1
        else:
            print(f"{index}: RUNNING: {cmd2}")
            os.system(cmd2)
            num_ran += 1

print(f"\n\nskipped: {num_skipped}, ran: {num_ran}.")
