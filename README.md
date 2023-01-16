# finitebwlc-experiments

## Download rules to consider

- Download all (Need to specify order or priority, e.g. BFS from genesis)
- Download towards freshest tip
- Download towards longest tip : CURRENT! For now: stay with this choice.
- Download towards longest tip that extends current longest downloaded chain

In case of download rules that download towards a tip: Downloading now continues towards lower priority tips after it is completed.

## Download pipeline

- Simple FIFO (1 block at a time towards the target) -> CURRENT!  *Staying with this choice*
- More advanced: Parallelized downloads (share bandwidth across multiple simultaneous downloads)

## Modeling choices

- Do we preempt active downloads? (currently yes)  *We need to explain in the paper how this differs from the analysis*
- Are partial block downloads saved? (currently yes -- there is a buffer of saved blocks)
- Headers take time to propagate. The time headers are received by a node after publication is node-specific so we can give attackers headers instantly.
- The current network model is simplistic. Not implementing P2P flooding at this time. Instead we are "downloading from cloud"

## Information to collect

- rate of growth of the main chain
- imbalance in number of blocks in chain between miners that have higher vs lower bandwidth?

## TODOs

- Implement an attacker node for PoS
- Implement equivocations and integrate mining rounds a-la-PoS

## Experiments to do

- PoS with misusing equivocations -> kills rate
- PoS with with download avoidance for exquivocations -> works well!

- how the different download rules compare?

Bonus if there is time

- how bandwidth differences affect miner rewards?