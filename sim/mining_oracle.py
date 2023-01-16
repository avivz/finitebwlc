from .node import Node
from typing import List, Generator
import random
import simpy.core
import simpy.events
import numpy.random


class PoWMiningOracle:
    def __init__(self, env: simpy.core.Environment, nodes: List[Node]):
        self.__nodes = nodes[:]
        self.__weights = [node.mining_rate for node in nodes]
        self.__total_mining_power = sum(self.__weights)
        self.__env = env

        # start the mining events:
        self.__env.process(self.run_mining())

    def run_mining(self) -> Generator[simpy.events.Timeout, None, None]:
        while True:
            time_to_next_block = get_time_to_next_block(
                self.__total_mining_power)
            yield (self.__env.timeout(time_to_next_block))

            # select miner by relative weight
            miner, = random.choices(self.__nodes, weights=self.__weights, k=1)
            miner.mine_block()


def get_time_to_next_block(lambda_param: float) -> float:
    return numpy.random.exponential(1/lambda_param)


class PoSMiningOracle:
    """in PoS mode, the mining power of each node is interpreted as the (inedpendent) probability that it mines at any given round."""

    def __init__(self, env: simpy.core.Environment, nodes: List[Node], round_length: float, starting_round: int):
        self.__nodes = nodes[:]
        self.__round_length = round_length
        self.__env = env

        # start the mining events:
        self.__env.process(self.run_mining(starting_round))

    def run_mining(self, starting_round: int) -> Generator[simpy.events.Timeout, None, None]:
        round = starting_round
        while True:
            round += 1
            yield (self.__env.timeout(self.__round_length))

            numpy.random.shuffle(self.__nodes)  # type: ignore
            coin_toss = numpy.random.random(len(self.__nodes))
            for i, miner in enumerate(self.__nodes):
                if coin_toss[i] < miner.mining_rate:
                    miner.mine_block()
