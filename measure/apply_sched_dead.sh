#!/bin/bash
DEADLINE_RUN=$1
DEADLINE_PERIOD=$2


VMPID=""

while [ -z "$VMPID" ]; do 
VMPID=$(pidof qemu-system-x86_64);
sleep 0.5; 
done; 

for vcore in $(ps -T -p $VMPID | awk 'NR==4 || NR==5 {print $2}'); do
    echo "HIII vcore $vcore"
    sudo chrt -d --sched-runtime $DEADLINE_RUN --sched-period $DEADLINE_PERIOD --sched-deadline $DEADLINE_RUN -p 0 $vcore
done
