import simpy.core
from sim.block import Block

# Globally available constants and simulation parameters
ENV = simpy.core.Environment()
GENESIS = Block(None, None, 0)
