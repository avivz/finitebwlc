from node import Node
from mining_oracle import PoWMiningOracle
from network import Network
import simpy.core


def run_experiment() -> None:
    """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
    env = simpy.core.Environment()

    network = Network(header_delay=0.1, env=env)
    nodes = [Node(1/10, 1, network) for _ in range(10)]
    oracle = PoWMiningOracle(nodes, env)
    env.process(oracle.run_mining())
    env.run(until=300)


if __name__ == "__main__":
    run_experiment()
