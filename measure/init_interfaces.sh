#!/bin/bash

. config_file

ssh $RUNNER_SSH << EOB

sudo modprobe -r kvm_intel
sudo modprobe kvm_intel

sudo brctl addbr virbr0
sudo ip link set virbr0 up

sudo ip addr flush dev $RUNNER_IFACE
sudo brctl addif virbr0 $RUNNER_IFACE
sudo ip addr add $RUNNER_IPERF dev virbr0
sudo ip link set $RUNNER_IFACE up

sudo ip tuntap add dev tap0 mode tap user $(whoami)
sudo ip link set tap0 up
sudo brctl addif virbr0 tap0

sudo ip link set tap0 master virbr0
sudo ip link set virbr0 up
sudo ip link set tap0 up

EOB