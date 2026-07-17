# BBR in Virtual Machines under CPU Contention

## Measurement Framework
This repository contains an emulation framework for measuring Linux TCP in Virtual Machines under CPU contention. For details, refer to our paper "2BRobust - Mitigating TCP BBR Performance Degradation in Virtual Machines under CPU Contention" accepted for the 2026 ACM CoNEXT.

<img width="1152" height="218" alt="framework" src="https://github.com/user-attachments/assets/a779c91d-8f66-40b1-87ed-379d657bc7ca" />

As shown in the figure above, the measurement framework consists of three physical machines:
- the "runner" which orchestrates the measurements and hosts the sender VM,
- the "emulator" which emuates different link conditions on the bottleneck link,
- and the TCP "receiver".

The setup, in particular host and interface names, are to be configured in [measure/config_file](measure/config_file).
The runner must have the folder `~/debianbuild/` containing a QEMU/KVM VM disk file, i.e., debian.qcow2.

## BBR Patches
Our BBRv1 and BBRv3 patches, as detailed in the paper, can be found in [patches/](patches).
