# BBR in Virtual Machines under CPU Contention

This repository contains artifacts and code contributions presented in our paper "2BRobust - Mitigating TCP BBR Performance Degradation in Virtual Machines under CPU Contention" accepted for the 2026 ACM CoNEXT.

## Measurement Framework
[measure/](measure) contains an emulation framework for measuring Linux TCP in Virtual Machines under CPU contention. For details, refer to our paper.

<img width="1152" height="218" alt="framework" src="https://github.com/user-attachments/assets/a779c91d-8f66-40b1-87ed-379d657bc7ca" />

As shown in the figure above, the measurement framework consists of three physical machines:
- the "runner" which orchestrates the measurements and hosts the sender VM,
- the "emulator" which bridges traffic between runner and receiver whilst emulating different link conditions on the outgoing interfaces,
- and the TCP "receiver".

The setup, in particular host and interface names, are to be configured in [measure/config_file](measure/config_file).
The runner must have the folder `~/debianbuild/` containing a QEMU/KVM VM disk file, i.e., debian.qcow2.

All scripts are to be run from a remote user with SSH access to the setup nodes.
Make sure to appropriately configure the local network of the experimental setup, including L2-bridging or IP forwarding on the emulator node.

After configuration, 
- run `bash init_interfaces.sh` to setup the TAP interface for the VM,
- add the desired run definitions in `run_multiple.sh`, and
- run `bash launch.sh` to start the execution of runs.

## BBR Patches
Our BBRv1 and BBRv3 patches, as detailed in the paper, can be found in [patches/](patches).


## Results
[results/](results) contains the final dataset and scripts used to produce the plots shown in the paper.

**How to reproduce**:
1) Clone, and extract dataset `results/data.tar.xz` (decompressed size: 584 MB).
2) Run the `results/plots/figure_*.ipynb` notebooks (tested with Python 3.12.3 kernel).
3) Pdf plots are generated into `results/plots/figures`. 
4) Some notebooks can generate multiple plots from the paper, e.g. `figure_7_14.ipynb`. Use the switch in the first code cell to control which figure is produced.


## License
- Code: MIT (see [LICENSE](./LICENSE))
- Data (`results/data.tar.xz`): CC-BY 4.0 (see [results/DATA_LICENSE](./results/DATA_LICENSE))
