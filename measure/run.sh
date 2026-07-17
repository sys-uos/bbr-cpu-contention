#!/bin/bash

KERNEL=$1
MODE=$2
LOSS=$3
BW=$4
RTT=$5
BUFFER=$6
SEED=$7
PARALLEL=${8}
CCA=${9}
DEADLINE_RUN=${10}
DEADLINE_PERIOD=${11}

. config_file

CPUS=2
N=4

if [ "$#" -lt 11 ]; then
    echo "Usage: bash run.sh KERNEL['kernel6-1', 'kernel6-4', 'BBRv3', 'kernel5-10', 'kernel4-19', 'BBRv2'] MODE['iperf3', 'scp'] LOSS['random 0.1 25', 'gemodel 0.1 95 50 0.01'] BANDWIDTH[in mbit] RTT[in ms] BUFFER[in BDP] (SEED) (PARALLEL) (CCA) (CPUS)"
    echo Example: bash run.sh BBRv3 iperf3 "none" 800 20 3.0 1740753059782645566 1740753063782943194 1.0 cubic net.core.default_qdisc=pfifo_fast
    exit -1
fi

LOSS_MODE=$(echo $LOSS |  awk '{print $1;}')
LOSS_PARAMS=$(echo $LOSS | cut -d " " -f 2-)

NETWORK_BUFFER_SIZE=$(python3 calculate_bdp.py --rate $BW --rtt $RTT --factor $BUFFER)
SOCKET_BUFFER_SIZE=2147483647

if [[ $KERNEL = "kernel6-1" ]]; then
  DISK="debian.qcow2"
elif [[ $KERNEL = "BBRv3" ]]; then
  DISK="bbr3_debian.qcow2"
elif [[ $KERNEL = "BBRv3_fixed" ]] || [[ $KERNEL = "BBRv3_fixed" ]]; then
  DISK="bbr3_fixed_debian.qcow2"
elif [[ $KERNEL = "BBRv3_fixed" ]]; then
  DISK="bbr3_fixed_debian_n2.qcow2"
elif [[ $KERNEL = "BBRv2" ]]; then
  DISK="bbr2_debian-11.qcow2"
elif [[ $KERNEL = "BBRv2_fixed" ]]; then
  DISK="debian-11.qcow2"
elif [[ $KERNEL = "kernel6-1_fixed" ]] || [[ $KERNEL = "kernel6-1_fixed" ]]; then
  DISK="fixed_debian.qcow2"
  echo "Fixed kernel"
else
  echo "Kernel not supported"
  exit 0
fi


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
# $RECEIVER_SSH runs a daemon iperf3 server...
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
                  --arg mode "$MODE" \
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
                  '{chaos: "on_1", deadline_run: $deadline_run, deadline_period: $deadline_period, os: "debian", bdp: $buffer_bdp, setup: "new", cca: $cca, cpus: $cpus, kernel: $kernel, mode: $mode, loss: {mode: $loss_mode, params: $loss_params, seed1: $seed}, rate: $bw, delay_rtt: $rtt, buffer_size_bytes: $buffer, parallel: $parallel, socket_buffer: "2147483647", app_buffer: "default", n: $n, sysctl_cmd: "", adapter_type: "virtio", vm: "qemu_kvm"}')

echo $JSON_CONFIG > ${LOGDIR}/meta.json

for ((i=1; i<=N; i++)); do
 scp $VM_SSH:iperf_$i.json ${LOGDIR}/sender/;
done

ssh $VM_SSH << EOB
 rm iperf_*.json
EOB

sudo killall qemu-system-x86_64

echo "All done!"