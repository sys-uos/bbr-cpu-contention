#!/bin/bash

sudo qemu-system-x86_64 \
    -enable-kvm \
    -drive file=$1,media=disk,if=virtio \
    -m 16G \
    -smp $2 -cpu host,-svm \
    -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
    -device virtio-net-pci,netdev=net0,mac=52:54:00:12:34:56 \
    -daemonize -display none

sleep 100