# finitebwlc-experiments

## Download rules to consider

- Download all (Need to specify order or priority, e.g. BFS from genesis)
- Download towards freshest tip
- Download towards longest tip : CURRENT! For now: stay with this choice.

In case of download rules that download towards a tip: Downloading now continues towards lower priority tips after it is completed.

## Download pipeline

- Simple FIFO (1 block at a time towards the target) -> CURRENT!  *Staying with this choice*
- More advanced: Parallelized downloads (share bandwidth across multiple simultaneous downloads)

## Modeling choices

- Do we preempt active downloads? (currently yes)  *We need to explain in the paper how this differs from the analysis*
- Are partial block downloads saved? (currently no)
- Headers take time to propagate. The time headers are received by a node after publication is node-specific so we can give attackers headers instantly.
- The current network model is simplistic. Not implementing P2P flooding at this time. Instead we are "downloading from cloud"

## Information to collect

- Mining power wasted (time honest nodes spent mining on tips that aren't longest chain at the time of mining). This is slightly different from fraction of blocks discarded if attacker is present
- Fraction of honest blocks in main chain

## TODOs

- Implement an attacker node (Strategy: For PoW: reveal tips to make chain longer but only make partial downloads possible)
- Implement a PoS mining oracle
- Collect information
- Implement information collection from parallelized experiments
- Plots!

## Plots to do

- beta (max adversary strength we are safe for) as a function of delay / bandwidth
- draw a time-line of actions for a node
