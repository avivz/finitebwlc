from node import Node
from mining_oracle import PoWMiningOracle
from network import Network
import simpy.core
import argparse
import simulation_parameters
import cProfile


def run_experiment() -> None:
    """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
    network = Network()

    num_nodes = 100
    total_block_rate = 1  # blocks per sec
    nodes = [Node(mining_rate=total_block_rate/num_nodes,
                  bandwidth=2,
                  header_delay=0.1,
                  network=network)
             for _ in range(num_nodes)]
    PoWMiningOracle(nodes)
    simulation_parameters.ENV.run(until=10_000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='basic_experiment',
        description='Run a basic experiment of the mining simulation')

    parser.add_argument('-v', '--verbose',
                        action='store_true', help="print events to stdout")  # on/off flag

    parser.add_argument('-p', '--profile',
                        action='store_true', help="run a profiler to time the execution")  # on/off flag

    args = parser.parse_args()
    simulation_parameters.verbose = args.verbose
    if args.profile:
        cProfile.run('run_experiment()')
    else:
        run_experiment()
