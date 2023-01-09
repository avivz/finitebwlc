# finitebwlc-experiments

## Download rules to consider

- Download all (Need to specify order or priority, e.g. BFS from genesis)
- Download towards freshest tip
- Download towards longest tip : CURRENT! For now: stay with this choice.

In case of download rules that download towards a tip: one must decide if downloading of secondry items is attempted once the tip has been reached. (currently no)
*Extend to download additional long chains once done*

## Download pipeline

- Simple FIFO (1 block at a time towards the target) -> CURRENT!  *Staying with this choice*
- More advanced: Parallelized with limited slots (e.g., 3 download slots that share bandwidth)

## Modeling questions

- Do we preempt active downloads? (currently yes)  *We need to explain in the paper how this differs from the analysis*
- Are partial block downloads saved? (currently no)
- Do headers take time to propagate? (currently yes) 
- How realistic is the network model? should I simulate P2P flooding, or download from a cloud? (currently downloading from cloud)

## Information to collect

- Mining power wasted (time honest nodes spent mining on tips that aren't longest chain at the time of mining). This is slightly different from fraction of blocks discarded if attacker is present. 
- Fraction of honest blocks in main chain

## TODOs

- Implement an attacker node (Strategy: For PoW: reveal tips to make chain longer but only make partial downloads possible)
- Add support for attacker revealing tips of chain selectively and witholding content selectively
- Implement a PoS mining oracle
- Collect information
- Implement information collection from parallelized experiments
- Plot 

# Plots to do:

- beta (max adversary strength we are safe for) as a function of delay / bandwidth
- draw the chain that is created
