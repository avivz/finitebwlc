# finitebwlc-experiments

## Requirements:
Python 3.7 or above.

## Installation:

At the root directory of the repository:
- Create a virtual environment: `> python3 -m venv env`
- Activate the environment: `> source env/bin/activate`
- Install requirements using `> pip install -r requirements.txt`

Then from the root project directory the following commands can be executed:
- `> python -m sim.run_experiment [OPTIONS]`   Will run a single simulation trace
- `> python -m exp_greedy.run [OPTIONS]`  Runs a set of experiments on the greedy rule
- `> python -m exp_greedy.collect [OPTIONS]` Collects the results from experiments
- `> python -m exp_teaser.run [OPTIONS]` Runs a set of experiments on the teasing attack
- `> python -m exp_teaser.collect [OPTIONS]` Collects the results from experiments


## Running an experiment
### To run an experiment
`> python -m exp_*.run [-h] --data_dir DATA_DIR [--slurm] [--no_out]`


optional arguments:
```
  -h, --help           show a help message and exit
  --data_dir DATA_DIR  where to save results within the data directory
  --slurm              runs the code in parallel on slurm using sbatch
  --no_out             runs the code in parallel on slurm using sbatch
```

### To analyze the results

`> python -m exp_*.collect [-h] [--logx] --data_dir DATA_DIR`


optional arguments:
```
  -h, --help           show a help message and exit
  --logx               makes x axis logscale
  --data_dir DATA_DIR  where to find results within the data directory
```

## Runing a single simulation trace:

```
> python -m run_experiment [-h] [--verbose] [--plot START END] [--induce_split START END] --mode {pos,pow} [--pos_round_length SECs] [--dumb_attacker MINING_POWER] [--teasing_attacker MINING_POWER] [--attacker_head_start NUM_BLOCKS] --run_time RUN_TIME [--download_rule {longest_header_chain,greedy_extend_chain}] --num_honest NUM_HONEST --honest_block_rate HONEST_BLOCK_RATE --bandwidth BANDWIDTH --header_delay HEADER_DELAY [--save_results SAVE_RESULTS]
```

Run a basic experiment of the mining simulation. Specify a configuration file with @<filename>.

Optional arguments:
```
  -h, --help            show a help message and exit
  --verbose             print events to stdout
  --plot START END      plot a block diagram from <START> to <END> times
  --induce_split START END 
                        split the network from <START> to <END> times
  --mode {pos,pow}      which mode of operation we are using
  --pos_round_length SECs
                        How long the mining round is in PoS (valid only in PoS mode, defaults to 1sec)
  --dumb_attacker MINING_POWER
                        include an attacker with the given mining power (defaults to no attacker)
  --teasing_attacker MINING_POWER
                        include a teasing attacker with the given mining power (defaults to no attacker)
  --attacker_head_start NUM_BLOCKS
                        give any attacker NUM_BLOCKS mining at the begining of the simulation. This only matters if an attacker is present.
  --run_time RUN_TIME   time to run
  --download_rule {longest_header_chain,greedy_extend_chain}
                        The download rule to use
  --num_honest NUM_HONEST
                        number of honest nodes
  --honest_block_rate HONEST_BLOCK_RATE
                        mining power of each honest node
  --bandwidth BANDWIDTH
                        bandwidth of each honest node
  --header_delay HEADER_DELAY
                        header_delay header delay of each honest node
  --save_results SAVE_RESULTS
                        filename (Where to save the results of the simulation)
```