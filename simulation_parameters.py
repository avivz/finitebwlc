import simpy.core
from block import Block

# Globally available constants and simulation parameters
verbose = False
ENV = simpy.core.Environment()
GENESIS = Block(None, None, 0)
