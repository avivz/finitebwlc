# finitebwlc-experiments

All download rules can be either:

- FIFO (1 block at a time towards the target)
- Parallelized (downloading in parallel towards the target)
- Parallelized with limited parallelism (e.g., 3 download slots that share bandwidth)

download rules to consider:

- Download all (Need to specify order or priority, e.g. BFS from genesis)
- Download towards freshest tip
- Download towards longest tip

In case of download rules that download towards a tip: one must decide if downloading of secondry items is attempted once the tip has been reached.

Modeling questions:

- Are partial block downloads saved?
- Do headers take time to propagate?
- How realistic is the network model? should I simulate P2P flooding, or download from a cloud?