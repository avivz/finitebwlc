from enum import Enum

# TODO do we need this?


class DownloadRules(Enum):
    LongestHeaderChain = "longest_header_chain"
    GreedyExtendChain = "greedy_extend_chain"
