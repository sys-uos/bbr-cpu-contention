# BBR in Virtual Machines under CPU Contention

## Measurement Framework
This repository contains an emulation framework for measuring Linux TCP in Virtual Machines under CPU contention. For details, refer to our paper "2BRobust - Mitigating TCP BBR Performance Degradation in Virtual Machines under CPU Contention" accepted for the 2026 ACM CoNEXT.

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
