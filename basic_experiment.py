from node import Node
from mining_oracle import PoWMiningOracle
from network import Network
import simpy.core
import argparse
import simulation_parameters


def run_experiment() -> None:
    """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
    env = simpy.core.Environment()
    network = Network(env=env)

    num_nodes = 100
    total_block_rate = 1  # blocks per sec
    nodes = [Node(mining_rate=total_block_rate/num_nodes,
                  bandwidth=2,
                  header_delay=0.1,
                  network=network)
             for _ in range(num_nodes)]
    PoWMiningOracle(nodes, env)
    env.run(until=10_000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Mining Simulation',
        description='Run a basic experiment of the mining simulation')

    parser.add_argument('-v', '--verbose',
                        action='store_true')  # on/off flag
    args = parser.parse_args()
    simulation_parameters.verbose = args.verbose
    run_experiment()
