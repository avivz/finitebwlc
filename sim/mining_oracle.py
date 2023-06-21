from .node import Node
from typing import List, Generator, Dict
import random
import simpy.core
import simpy.events
import simpy.exceptions
import numpy.random


class PoWMiningOracle:
    def __init__(self, env: simpy.core.Environment):
        self.__nodes: List[Node] = []
        self.__weights: List[float] = []
        self.__total_mining_power: float = 0.0
        self.__env = env

        # start the mining events:
        self.__mining_process = self.__env.process(self.run_mining())

    def add_node(self, node: Node) -> None:
        self.__nodes.append(node)
        self.__total_mining_power += node.mining_rate
        self.__weights.append(node.mining_rate)
        self._reschedule_next_block()

    def remove_node(self, node: Node) -> None:
        ind = self.__nodes.index(node)
        self.__nodes.pop(ind)
        self.__total_mining_power -= node.mining_rate
        self.__weights.pop(ind)
        self._reschedule_next_block()

    def _reschedule_next_block(self) -> None:
        # interrupt the current mining process:
        if self.__mining_process.is_alive:
            self.__mining_process.interrupt()
        else:
            self.__mining_process = self.__env.process(self.run_mining())

    def run_mining(self) -> Generator[simpy.events.Timeout, None, None]:
        while True:
            if self.__total_mining_power <= 0:
                return

            time_to_next_block = get_time_to_next_block(
                self.__total_mining_power)
            try:
                yield (self.__env.timeout(time_to_next_block))

                # select miner by relative weight
                miner, = random.choices(
                    self.__nodes, weights=self.__weights, k=1)
                miner.mine_block()
            except simpy.exceptions.Interrupt as interrupt:
                pass  # restart the loop if interrupted, using the new weights


def get_time_to_next_block(lambda_param: float) -> float:

    return numpy.random.exponential(1/lambda_param)
