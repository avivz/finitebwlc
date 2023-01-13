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
    return parser


BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
SIMULATION_PATH = os.path.join(BASE_PATH, "src/run_experiment.py")

PYTHON_PATH = "python"

OUTPUT_PATH = os.path.join(BASE_PATH, "experiment_honest_growth/data/")

base_arguments = ["--time 2000", "--num_honest 100",
                  "--pow_honest 0.01"]  # "--header_delay 0"  "--bandwidth -1"

bandwidth_range = numpy.arange(0.1, 4.2, 0.05)

parser = setup_parser()
args = parser.parse_args()

for index, bandwidth in enumerate(bandwidth_range):
    file_name1 = os.path.join(OUTPUT_PATH, "exp1_band_" + str(index)+".json")
    arguments1 = base_arguments + \
        [f"--header_delay 0 --bandwidth {bandwidth}",
            f"--saveResults {file_name1}"]

    file_name2 = os.path.join(OUTPUT_PATH, "exp1_delay_" + str(index)+".json")
    arguments2 = base_arguments + \
        [f"--header_delay {1/bandwidth} --bandwidth -1",
            f"--saveResults {file_name2}"]

    cmd1 = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments1)}"
    cmd2 = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments2)}"

    if args.slurm:
        cmd1 = f'sbatch --mem=8g -c1 --wrap="{cmd1}"'
        cmd2 = f'sbatch --mem=8g -c1 --wrap="{cmd2}"'

    print(f"{index}: running:\n\t{cmd1}")
    os.system(cmd1)
    print(f"{index}: running:\n\t{cmd2}")
    os.system(cmd2)
