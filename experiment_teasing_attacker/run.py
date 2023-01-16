#!/usr/bin/python3
import numpy
import os
import argparse
from typing import List
import tqdm


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

OUTPUT_PATH = os.path.join(BASE_PATH, "experiment_teasing_attacker/data/")

base_arguments = ["--run_time 10000", "--num_honest 100", "--mode pow"
                  "--pow_honest 0.01", "--header_delay 0"]

bandwidth_range = numpy.arange(0.05, 2, 0.05)
num_repetitions = 100

parser = setup_parser()
args = parser.parse_args()

num_skipped = 0

if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

commands_to_run: List[str] = []

for index, bandwidth in enumerate(bandwidth_range):
    for rep in range(num_repetitions):
        file_name1 = os.path.join(
            OUTPUT_PATH, "exp2_band_" + str(index)+"_"+str(rep)+".json")
        arguments1 = base_arguments + \
            [f"--bandwidth {bandwidth}",
                f"--saveResults {file_name1}"]

        file_name2 = os.path.join(
            OUTPUT_PATH, "exp2_teaser_" + str(index)+"_"+str(rep)+".json")
        arguments2 = arguments1 + \
            [f"--saveResults {file_name2}",
                "--teasing_attacker 1.0", "--attacker_head_start 100"]

        cmd1 = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments1)}"
        cmd2 = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments2)}"

        if os.path.exists(file_name1) and os.path.getsize(file_name1) > 0:
            print(f"SKIPPING {file_name1}")
            num_skipped += 1
        else:
            commands_to_run.append(cmd1)
        if os.path.exists(file_name2) and os.path.getsize(file_name2) > 0:
            print(f"SKIPPING {file_name2}")
            num_skipped += 1
        else:
            commands_to_run.append(cmd2)


if args.slurm:
    commands_to_run = [
        f'sbatch --mem=8g -c1 --wrap="{cmd}"' for cmd in commands_to_run]
    if args.no_out:
        commands_to_run = [
            cmd + ' --output=/dev/null' for cmd in commands_to_run]

for command in tqdm.tqdm(commands_to_run):
    print(f"RUNNING: {command}")

    os.system(command)

print(f"\n\nskipped: {num_skipped}, ran: {len(commands_to_run)}.")
