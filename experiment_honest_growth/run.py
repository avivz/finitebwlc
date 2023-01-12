import sys
import os

BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
SIMULATION_PATH = os.path.join(BASE_PATH, "src/run_experiment.py")

ENV_ACTIVATE_PATH = os.path.join(BASE_PATH, "env/bin/activate")
PYTHON_PATH = os.path.join(BASE_PATH, "env/bin/python")

arguments = ["--time 100",
"--num_honest 100", 
"--pow_honest 0.01", 
"--bandwidth 2", 
"--header_delay 0.1", "-v"]

cmd = f"{PYTHON_PATH} {SIMULATION_PATH} {' '.join(arguments)}"
print(cmd)
os.system(cmd)
