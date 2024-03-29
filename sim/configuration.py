import dataclasses
from typing import Optional, Tuple, ClassVar
from enum import Enum


class DownloadRules(Enum):
    LongestHeaderChain = "longest_header_chain"
    GreedyExtendChain = "greedy_extend_chain"


@dataclasses.dataclass
class RunConfig:
    MODE: ClassVar[str] = "mode"
    mode: str = "pow"

    POS_ROUND_LENGTH: ClassVar[str] = "pos_round_length"
    pos_round_length: float = 1

    RUN_TIME: ClassVar[str] = "run_time"
    run_time: float = 100

    NUM_HONEST: ClassVar[str] = "num_honest"
    num_honest: int = 1

    NUM_SPV: ClassVar[str] = "num_spv"
    num_spv: int = 0

    HONEST_BLOCK_RATE: ClassVar[str] = "honest_block_rate"
    honest_block_rate: float = 1

    BANDWIDTH: ClassVar[str] = "bandwidth"
    bandwidth: float = 1

    HEADER_DELAY: ClassVar[str] = "header_delay"
    header_delay: float = 0

    INDUCE_SPLIT: ClassVar[str] = "induce_split"
    induce_split: Optional[Tuple[float, float]] = None

    DUMB_ATTACKER: ClassVar[str] = "dumb_attacker"
    dumb_attacker: float = 0

    PRIVATE_ATTACKER: ClassVar[str] = "private_attacker"
    private_attacker: float = 0

    TEASING_ATTACKER: ClassVar[str] = "teasing_attacker"
    teasing_attacker: float = 0

    EQUIVOCATION_TEASING_ATTACKER: ClassVar[str] = "equivocation_teasing_attacker"
    equivocation_teasing_attacker: float = 0

    ATTACKER_HEAD_START: ClassVar[str] = "attacker_head_start"
    attacker_head_start: int = 0

    DOWNLOAD_RULE: ClassVar[str] = "download_rule"
    download_rule: str = DownloadRules.LongestHeaderChain.value

    PLOT: ClassVar[str] = "plot"
    plot: Optional[Tuple[float, float]] = None

    SAVE_RESULTS: ClassVar[str] = "save_results"
    save_results: str = ""

    LOG_BLOCKS: ClassVar[str] = "log_blocks"
    log_blocks: str = ""

    VERBOSE: ClassVar[str] = "verbose"
    verbose: bool = False


if __name__ == "__main__":
    print([field.name for field in dataclasses.fields(RunConfig)])
