#!/usr/bin/python3
import numpy
import os
import argparse
from typing import List
import tqdm
from p_tqdm import p_umap
import sim.configuration


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='run',
        description='Runs the experiment',
        fromfile_prefix_chars='@')

    parser.add_argument('--data_dir',
                        nargs=1, help="where to save results within the data directory", required=True, type=str)

    parser.add_argument('--slurm',
                        action='store_true', help="runs the code in parallel on slurm using sbatch")  # on/off flag
    parser.add_argument('--no_out',
                        action='store_true', help="runs the code in parallel on slurm using sbatch")  # on/off flag
    return parser


BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
SIMULATION_MODULE = "sim.run_experiment"

PYTHON_PATH = "python"

DATA_ROOT_PATH = os.path.join(os.path.split(
    os.path.abspath(__file__))[0], "data/")
if not os.path.exists(DATA_ROOT_PATH):
    os.mkdir(DATA_ROOT_PATH)

parser = setup_parser()
args = parser.parse_args()

DATA_PATH = os.path.join(DATA_ROOT_PATH, args.data_dir[0])
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)

base_arguments = [f"--{sim.configuration.RunConfig.RUN_TIME} 10000", f"--{sim.configuration.RunConfig.NUM_HONEST} 100", f"--{sim.configuration.RunConfig.MODE} pow",
                  f"--{sim.configuration.RunConfig.HONEST_BLOCK_RATE} 0.01", f"--{sim.configuration.RunConfig.HEADER_DELAY} 0"]


# # linear1
# bandwidth_range = numpy.arange(0.1, 2.001, 0.20)
# num_repetitions = 10

# linear2
bandwidth_range = numpy.arange(0.1, 2.001, 0.05)
num_repetitions = 100


num_skipped = 0
commands_to_run: List[str] = []

for rep in range(num_repetitions):
    for index, bandwidth in enumerate(bandwidth_range):
        file_name1 = os.path.join(
            DATA_PATH, "exp2_band_" + str(index)+"_"+str(rep)+".json")
        arguments1 = base_arguments + \
            [f"--{sim.configuration.RunConfig.BANDWIDTH} {bandwidth}",
                f"--{sim.configuration.RunConfig.SAVE_RESULTS} {file_name1}"]

        file_name2 = os.path.join(
            DATA_PATH, "exp2_teaser_" + str(index)+"_"+str(rep)+".json")
        arguments2 = arguments1 + \
            [f"--{sim.configuration.RunConfig.SAVE_RESULTS} {file_name2}",
                f"--{sim.configuration.RunConfig.TEASING_ATTACKER} 1.0", f"--{sim.configuration.RunConfig.ATTACKER_HEAD_START} 100"]

        file_name3 = os.path.join(
            DATA_PATH, "exp2_teaser_equiv_" + str(index)+"_"+str(rep)+".json")
        arguments3 = arguments1 + \
            [f"--{sim.configuration.RunConfig.SAVE_RESULTS} {file_name3}",
                f"--{sim.configuration.RunConfig.EQUIVOCATION_TEASING_ATTACKER} 1.0", f"--{sim.configuration.RunConfig.ATTACKER_HEAD_START} 100"]

        cmd1 = f"{PYTHON_PATH} -m {SIMULATION_MODULE} {' '.join(arguments1)}"
        cmd2 = f"{PYTHON_PATH} -m {SIMULATION_MODULE} {' '.join(arguments2)}"
        cmd3 = f"{PYTHON_PATH} -m {SIMULATION_MODULE} {' '.join(arguments3)}"

        # # (note that we already have those values from exp_teaser ...)
        # if os.path.exists(file_name1) and os.path.getsize(file_name1) > 0:
        #     print(f"SKIPPING {file_name1}")
        #     num_skipped += 1
        # else:
        #     commands_to_run.append(cmd1)

        # # (note that we already have those values from exp_teaser ...)
        # if os.path.exists(file_name2) and os.path.getsize(file_name2) > 0:
        #     print(f"SKIPPING {file_name2}")
        #     num_skipped += 1
        # else:
        #     commands_to_run.append(cmd2)

        if os.path.exists(file_name3) and os.path.getsize(file_name3) > 0:
            print(f"SKIPPING {file_name3}")
            num_skipped += 1
        else:
            commands_to_run.append(cmd3)


if args.slurm:
    commands_to_run = [
        f'sbatch --mem=8g -c1 --wrap="{cmd}"' for cmd in commands_to_run]
    if args.no_out:
        commands_to_run = [
            cmd + ' --output=/dev/null' for cmd in commands_to_run]


def run_command(command):
    print(f"RUNNING: {command}")
    os.system(command)


p_umap(run_command, commands_to_run)


print(f"\n\nskipped: {num_skipped}, ran: {len(commands_to_run)}.")
