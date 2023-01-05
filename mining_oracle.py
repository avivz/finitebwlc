from node import Node
from typing import List, Generator
import random
import simpy.core
import numpy.random


class PoWMiningOracle:
    def __init__(self, nodes: List[Node]):
        self.__nodes = nodes[:]
        self.__weights = [node.mining_rate for node in nodes]
        self.__total_mining_power = sum(self.__weights)

    def mine(self, env: simpy.core.Environment) -> Generator[simpy.events.Timeout, None, None]:
        while True:
            time_to_next_block = get_time_to_next_block(
                self.__total_mining_power)
            yield (env.timeout(time_to_next_block))

            # select miner by relative weight
            miner, = random.choices(self.__nodes, weights=self.__weights, k=1)
            miner.mine_block()


def get_time_to_next_block(lambda_param: float) -> float:
    return numpy.random.exponential(1/lambda_param)
