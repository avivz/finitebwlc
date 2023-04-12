
from .block import Block
from .node import Node
import sim.network as network


class EquivocationTeasingPoWAttacker(Node):
    """this attacker mines on its own chains. As it receives blocks from the network,
    it always releases *an equivocating chain* with 2 headers ahead but allows download only one header ahead
    thus, a node that downloads towards the longest tip always first downloads *equivocating* block of this attacker
    up to the height matching the new honest block."""

    def __init__(self, genesis: Block, mining_rate: float, network: network.Network) -> None:
        super().__init__(genesis, mining_rate, bandwidth=0, header_delay=0, network=network)
        self._tip = genesis
        # this is the tip of the chain this node has allowed others to download.
        self._last_available = genesis
        self._num_interventions = 0
        self._highest_equivocation = 0

    def mine_block(self) -> Block:
        block = super().mine_block()
        block.is_available = False

        self._mining_target = block
        self._tip = block
        return block

    def receive_header(self, block: Block) -> None:
        super().receive_header(block)
        self._mining_target = self._tip

        # print(block, block.height, self._mining_target,
        #       self._mining_target.height)

        if block.height > self._highest_equivocation:
            if self._mining_target.height < block.height + 1:
                # Adversary's mining target is not higher than the new block, so no material to tease with
                # print("OOPS")
                pass
            else:
                # Opposite of above
                newtip = self._duplicate_and_announce_adversarial_chain_to_height(
                    self._mining_target, block.height + 1)
                # print('=>', newtip)
                self._highest_equivocation = block.height

        # self._num_interventions += 1
        # if self._num_interventions == 20:
        #     print("Blocktree:")
        #     print("digraph G {")
        #     for block in Block.all_blocks:
        #         print(
        #             f"  blk_{block.id.replace('.', '_')} [label=\"{block.id} of {block.miner.id if block.miner else None} at {round(block.creation_time, 2)} is {block.is_available}\"]")
        #         if block.parent:
        #             print(
        #                 f"  blk_{block.id.replace('.', '_')} -> blk_{block.parent.id.replace('.', '_')}")
        #     print("}")
        #     exit(0)

    def _duplicate_and_announce_adversarial_chain_to_height(self, blk, target_height) -> Block:
        while blk.height > target_height:
            blk = blk.parent

        blks_to_dup = []
        while blk.miner == self:
            blks_to_dup.append(blk)
            blk = blk.parent

        blk_parent = blk
        while len(blks_to_dup) > 0:
            blk_to_dup = blks_to_dup.pop()
            blk_new = Block(self, blk_parent,
                            EquivocationTeasingPoWAttacker.env.now)
            blk_parent = blk_new

            if blk_new.height < target_height - 1:
                blk_new.is_available = True
                self._broadcast_header(blk_new)
            elif blk_new.height <= target_height:
                blk_new.is_available = False
                self._broadcast_header(blk_new)

        return blk_parent

    def download_complete(self, block: Block) -> None:
        super().download_complete(block)
        self._mining_target = self._tip

    def download_interrupted(self, block: Block, fraction_downloaded: float) -> None:
        super().download_interrupted(block, fraction_downloaded)
        self._mining_target = self._tip
