# finitebwlc-experiments

All download rules can be either:

- Simple FIFO (1 block at a time towards the target) -> CURRENT!
- More advanced: Parallelized with limited slots (e.g., 3 download slots that share bandwidth)

download rules to consider:

- Download all (Need to specify order or priority, e.g. BFS from genesis)
- Download towards freshest tip
- Download towards longest tip : CURRENT!

In case of download rules that download towards a tip: one must decide if downloading of secondry items is attempted once the tip has been reached. (currently no)

Modeling questions:

- Do we preempt active downloads? (currently yes)
- Are partial block downloads saved? (currently no)
- Do headers take time to propagate? (currently yes)
- How realistic is the network model? should I simulate P2P flooding, or download from a cloud? (currently downloading from cloud)