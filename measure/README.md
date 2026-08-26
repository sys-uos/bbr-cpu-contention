## Measure
measure contains an emulation framework for measuring Linux TCP in Virtual Machines under CPU contention. For details, refer to our paper.

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


## Requirements
### Install on measurement machine (Debian/Ubuntu, not tested on other distributions)
```bash
sudo apt update
sudo apt install qemu-system-x86 qemu-utils qemu-kvm libvirt-daemon-system jq
```

### Running a VM with QEMU + KVM
- Download example VM disk file [here](https://myshare.uni-osnabrueck.de/f/b85674df472b4c38b992/?dl=1), or create your own one.
- Check your CPU supports virtualization (VT-x/AMD-V) and it's enabled in BIOS/UEFI:
  ```bash
  egrep -c '(vmx|svm)' /proc/cpuinfo
  ```
  (Output > 0 means supported.)
- Grant KVM access: Add your user to the `kvm` group so you don't need root to access `/dev/kvm`:
  ```bash
  sudo usermod -aG kvm $USER
  ```
  Log out and back in for this to take effect.
- Verify KVM is available:
  ```bash
  ls -l /dev/kvm
  ```
