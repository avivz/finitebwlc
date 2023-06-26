#!/usr/bin/python3
import numpy
import os
import argparse
from typing import List
import tqdm
import sim.configuration


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
DATA_DIR = "private_exp2"
PYTHON_PATH = "python"

DATA_ROOT_PATH = os.path.join(os.path.split(
    os.path.abspath(__file__))[0], "data/")
if not os.path.exists(DATA_ROOT_PATH):
    os.mkdir(DATA_ROOT_PATH)

parser = setup_parser()
args = parser.parse_args()

DATA_PATH = os.path.join(DATA_ROOT_PATH, DATA_DIR)
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)

block_rate = 1/2
bandwidth = 1
attacker_rates = [0.45, 0.4, 0.35, 0.3]
num_honest = 100
num_repetitions = 10


base_arguments = [f"--{sim.configuration.RunConfig.RUN_TIME} 2000", f"--{sim.configuration.RunConfig.NUM_HONEST} {num_honest}", f"--{sim.configuration.RunConfig.MODE} pow",
                  f"--{sim.configuration.RunConfig.HEADER_DELAY} 0"]

skip_count = 0
commands_to_run: List[str] = []

for rep in range(num_repetitions):
    for index, attacker_rate in enumerate(attacker_rates):
        results_file_name = os.path.join(
            DATA_PATH, "exp_private_start_" + str(index)+"_"+str(rep)+".json")
        block_log_file_name = os.path.join(
            DATA_PATH, "exp_private_start_" + str(index)+"_"+str(rep)+".log")

        arguments = base_arguments + [f"--{sim.configuration.RunConfig.BANDWIDTH} {bandwidth}",
                                      f"--{sim.configuration.RunConfig.HONEST_BLOCK_RATE} {(1-attacker_rate)*block_rate/num_honest}",
                                      f"--{sim.configuration.RunConfig.PRIVATE_ATTACKER} {attacker_rate*block_rate}",
                                      f"--{sim.configuration.RunConfig.SAVE_RESULTS} {results_file_name}",
                                      f"--{sim.configuration.RunConfig.LOG_BLOCKS} {block_log_file_name}",
                                      ]

        cmd = f"{PYTHON_PATH} -m {SIMULATION_MODULE} {' '.join(arguments)}"

        if os.path.exists(results_file_name) and os.path.getsize(results_file_name) > 0:
            print(f"SKIPPING {results_file_name}")
            skip_count += 1
        else:
            commands_to_run.append(cmd)


if args.slurm:
    commands_to_run = [
        f'sbatch --mem=8g -c1 --wrap="{cmd}"' for cmd in commands_to_run]
    if args.no_out:
        commands_to_run = [
            cmd + ' --output=/dev/null' for cmd in commands_to_run]

for command in tqdm.tqdm(commands_to_run):
    print(f"RUNNING: {command}")

    os.system(command)

print(f"\n\nskipped: {skip_count}, ran: {len(commands_to_run)}.")

# Sample run command:
# python -m exp_teaser_start.run_private_exp2
