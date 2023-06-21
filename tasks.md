# Refactoring to network simulation

- reach stable version that runs:
  - first version of block notification and request: notify of blocks, then request from first notifier, wait till it answers
  - notifier: Answers requests one after the other. sends full block then continues.
  - remember to randomly reorder notifications to achieve more stochasticity. 
- regain the ability to run the previous experiments via scripts to generate a json config file
- refactor out the slurm code
- refactor the timeline code out from "experiment"


## decisions on networking model:
1. Is there cap on node bandwidth or just per connection?
1. Is there an upload queue? how is it handled?
1. what if there is a request to dl a block and no dl starts? should we request from another? are other notifiers better?
1. are blocks downloaded in parallel from multiple connections, or in units?