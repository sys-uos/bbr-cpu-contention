#!/bin/bash

DISK=$1
LOSS=$2
BW=$3
RTT=$4
BUFFER=$5
SEED=$6
PARALLEL=$7
CCA=$8
DEADLINE_RUN=$9
DEADLINE_PERIOD=${10}

. config_file

CPUS=2
N=4

if [ "$#" -lt 10 ]; then
    echo "Usage: bash run.sh DISK[e.g. foo.qcow2] LOSS['none', 'random 0.1 25', 'gemodel 0.1 95 50 0.01'] BANDWIDTH[in mbit] RTT[in ms] BUFFER[in BDP] SEED PARALLEL CCA SCHED_DEADLINE_RUN[in ns] SCHED_DEADLINE_PERIOD[in ns]"
    echo Example: bash run.sh debian.qcow2 "none" 100 20 1.0 1740753059782645566 1.0 cubic 10000000 50000000
    exit -1
fi

LOSS_MODE=$(echo $LOSS |  awk '{print $1;}')
LOSS_PARAMS=$(echo $LOSS | cut -d " " -f 2-)

NETWORK_BUFFER_SIZE=$(python3 calculate_bdp.py --rate $BW --rtt $RTT --factor $BUFFER)
SOCKET_BUFFER_SIZE=2147483647

printf "\n"
echo "Start measurement..."
echo "Assumes that sudo does not require a password, make sure to add '<USER> ALL=(ALL) NOPASSWD: ALL' to sudo visudo"

printf "\n"
echo "Create folder..."
LOGDIR="logs/$(date +"%Y%m%d-%H%M%S")"
mkdir -p ${LOGDIR}
mkdir ${LOGDIR}/sender
mkdir ${LOGDIR}/emulator

printf "\n"
echo "Prepare emulator..."
scp setup_emulator.sh $EMULATOR_SSH:
scp calculate_bdp.py $EMULATOR_SSH:
ssh $EMULATOR_SSH -o LogLevel=FATAL << EOA
sudo bash setup_emulator.sh $EMULATOR_IFACE_LEFT $EMULATOR_IFACE_RIGHT $BW $NETWORK_BUFFER_SIZE $RTT $LOSS_MODE "$LOSS_PARAMS" $SEED
EOA

printf "\n"
echo "Prepare receiver..."
ssh $RECEIVER_SSH -o LogLevel=FATAL << EOB
sudo rm -rf /tmp/*
sudo sysctl -w net.core.rmem_max=$SOCKET_BUFFER_SIZE
sudo sysctl -w net.core.wmem_max=$SOCKET_BUFFER_SIZE
sudo sysctl -w net.ipv4.tcp_rmem="4096 131072 $SOCKET_BUFFER_SIZE"
sudo sysctl -w net.ipv4.tcp_wmem="4096 16384 $SOCKET_BUFFER_SIZE"
nohup iperf3 > tmp.log 2> tmp.log &
EOB

echo "Prepare sender (centaur03)..."
sudo sysctl -w net.core.rmem_max=$SOCKET_BUFFER_SIZE
sudo sysctl -w net.core.wmem_max=$SOCKET_BUFFER_SIZE
sudo sysctl -w net.ipv4.tcp_rmem="4096 131072 $SOCKET_BUFFER_SIZE"
sudo sysctl -w net.ipv4.tcp_wmem="4096 16384 $SOCKET_BUFFER_SIZE"
sudo sysctl -w net.ipv4.tcp_window_scaling=1

cd debianbuild

# launch new VM
sudo killall qemu-system-x86_64
sleep 1

sudo bash qemu.sh $DISK $CPUS

cd ..

# deadline scheduling
bash apply_sched_dead.sh $DEADLINE_RUN $DEADLINE_PERIOD &
sleep 1

ssh $VM_SSH << EOB
 rm iperf_*.json
 
 sysctl -w net.core.rmem_max=$SOCKET_BUFFER_SIZE
 sysctl -w net.core.wmem_max=$SOCKET_BUFFER_SIZE
 sysctl -w net.ipv4.tcp_rmem="4096 131072 $SOCKET_BUFFER_SIZE"
 sysctl -w net.ipv4.tcp_wmem="4096 16384 $SOCKET_BUFFER_SIZE"
 sysctl -w net.ipv4.tcp_window_scaling=1
 
 if [[ $KERNEL = "kernel6-1_fixed" ]] || [[ $KERNEL = "BBRv3_fixed" ]]; then
  modprobe -r tcp_bbr
  insmod tcp_bbr.ko   # register custom BBR module
 else
  modprobe tcp_bbr
  modprobe tcp_bbr2
 fi

 if [[ $CCA != "cubic" ]]; then
  sysctl -w net.ipv4.tcp_allowed_congestion_control="$CCA cubic"
 fi

 
 LIMIT=$N
 for ((i=1; i<=LIMIT; i++)); do
  sleep 1
  taskset -c 0 iperf3 -c $RECEIVER_IPERF --json --congestion ${CCA} --logfile iperf_\$i.json -t 20 -P ${PARALLEL};
 done

 sleep 3
EOB


JSON_CONFIG=$( jq -n \
                  --arg buffer_bdp "$BUFFER" \
                  --arg kernel "$KERNEL" \
                  --arg cca "$CCA" \
                  --arg loss_mode "$LOSS_MODE" \
                  --arg loss_params "$LOSS_PARAMS" \
                  --arg bw "$BW" \
                  --arg rtt "$RTT" \
                  --arg buffer "$NETWORK_BUFFER_SIZE" \
                  --arg seed "$SEED" \
                  --arg parallel "$PARALLEL" \
                  --arg n "$N" \
                  --arg cpus "$CPUS" \
                  --arg deadline_run "$DEADLINE_RUN" \
                  --arg deadline_period "$DEADLINE_PERIOD" \
                  '{chaos: "on_1", deadline_run: $deadline_run, deadline_period: $deadline_period, os: "debian", bdp: $buffer_bdp, setup: "new", cca: $cca, cpus: $cpus, kernel: $kernel, mode: iperf3, loss: {mode: $loss_mode, params: $loss_params, seed1: $seed}, rate: $bw, delay_rtt: $rtt, buffer_size_bytes: $buffer, parallel: $parallel, socket_buffer: "2147483647", app_buffer: "default", n: $n, sysctl_cmd: "", adapter_type: "virtio", vm: "qemu_kvm"}')

echo $JSON_CONFIG > ${LOGDIR}/meta.json

for ((i=1; i<=N; i++)); do
 scp $VM_SSH:iperf_$i.json ${LOGDIR}/sender/;
done

ssh $VM_SSH << EOB
 rm iperf_*.json
EOB

sudo killall qemu-system-x86_64

echo "All done!"