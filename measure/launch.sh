#!/bin/bash

. config_file

scp config_file $RUNNER_SSH:
scp run_multiple.sh $RUNNER_SSH:
scp run.sh $RUNNER_SSH:
scp start_qemu.sh $RUNNER_SSH:debianbuild/qemu.sh

scp setup_emulator.sh $RUNNER_SSH: 
scp calculate_bdp.py $RUNNER_SSH:

scp apply_sched_dead.sh $RUNNER_SSH:

ssh $RUNNER_SSH -o LogLevel=FATAL << EOB
 nohup bash run_multiple.sh > tmp.log 2> tmp.log &
EOB