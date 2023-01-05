from node import Node
from mining_oracle import PoWMiningOracle
import simpy


def run_experiment() -> None:
    """a basic experiment with 10 nodes mining together at a rate of 1 block per second"""
    nodes = [Node(1/10, 1) for _ in range(10)]
    oracle = PoWMiningOracle(nodes)
    env = simpy.Environment()  # type: ignore

    env.process(oracle.mine(env))
    env.run(until=300)


if __name__ == "__main__":
    run_experiment()
