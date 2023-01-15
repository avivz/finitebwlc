#!/usr/bin/python3
import numpy
import os
import argparse


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
SIMULATION_PATH = os.path.join(BASE_PATH, "src/run_experiment.py")

PYTHON_PATH = "python"

OUTPUT_PATH = os.path.join(BASE_PATH, "experiment_honest_growth/data/")

base_arguments = ["--run_time 10000", "--num_honest 100",
                  "--pow_honest 0.01"]  # "--header_delay 0"  "--bandwidth -1"

bandwidth_range = numpy.arange(0.1, 4.2, 0.05)
num_repetitions = 10

parser = setup_parser()
args = parser.parse_args()

num_skipped = 0
num_ran = 0

for index, bandwidth in enumerate(bandwidth_range):
    for rep in range(num_repetitions):
        file_name1 = os.path.join(
            OUTPUT_PATH, "exp1_band_" + str(index)+"_"+str(rep)+".json")
        arguments1 = base_arguments + \
            [f"--header_delay 0 --bandwidth {bandwidth}",
                f"--saveResults {file_name1}"]

        file_name2 = os.path.join(
            OUTPUT_PATH, "exp1_delay_" + str(index)+"_"+str(rep)+".json")
        arguments2 = base_arguments + \
            [f"--header_delay {1/bandwidth} --bandwidth -1",
                f"--saveResults {file_name2}"]

        cmd1 = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments1)}"
        cmd2 = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments2)}"

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
