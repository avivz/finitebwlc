#!/usr/bin/python3
import numpy
import os

BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
SIMULATION_PATH = os.path.join(BASE_PATH, "src/run_experiment.py")

ENV_ACTIVATE_PATH = os.path.join(BASE_PATH, "env/bin/activate")
PYTHON_PATH = os.path.join(BASE_PATH, "env/bin/python")

OUTPUT_PATH = os.path.join(BASE_PATH, "experiment_honest_growth/data/")

base_arguments = ["--time 1000","--num_honest 100", "--pow_honest 0.01", "--header_delay 0"]



bandwidth_range = numpy.arange(0.1,4.2,1)
for index, bandwidth in enumerate(bandwidth_range):
    file_name = os.path.join(OUTPUT_PATH, "exp1_" + str(index))
    arguments = base_arguments + [f"--bandwidth {bandwidth}", f"--saveResults {file_name}"]
    cmd = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments)}"
    sbatch_cmd = f'sbatch --mem=1g -c1 --wrap="{cmd}"'
    print(f"{index}: running:\n\t{cmd}")
    os.system(cmd)
print(cmd)
