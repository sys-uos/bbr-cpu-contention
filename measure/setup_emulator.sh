#!/bin/bash

# Setup emulator
# to support seeded loss, iproute2 package version v6.6.0 or higher is required

EMULATOR_IFACE_LEFT=$1
EMULATOR_IFACE_RIGHT=$2
RATE=$3
BUFFER_SIZE=$4
RTT=$5
LOSS_MODE=$6
LOSS_PARAMS=$7
SEED=$8

sudo ethtool -K $EMULATOR_IFACE_LEFT tso on
sudo ethtool -K $EMULATOR_IFACE_LEFT gso on
sudo ethtool -K $EMULATOR_IFACE_LEFT gro on
sudo ethtool -K $EMULATOR_IFACE_RIGHT tso on
sudo ethtool -K $EMULATOR_IFACE_RIGHT gso on
sudo ethtool -K $EMULATOR_IFACE_RIGHT gro on

iproute2_seed_support() {
    local required="6.6.0"
    local current

    current=$(tc -V | sed -n 's/.*iproute2-\([0-9.]*\).*/\1/p') || return 1
    [ -n "$current" ] || return 1

    [ "$(printf '%s\n%s\n' "$required" "$current" | sort -V | head -n1)" = "$required" ]
}


if [[ $1 == "-h"  || "$#" < 6 ]]; then
    echo "Usage: bash setup_emulator.sh [Bandwidth in Mbps] [Buffer size in bytes] [RTT in ms] [loss mode] [loss parameter] [Seed]"
    echo "Example: bash setup_emulator.sh 500 625000 100 random \"0.1\" 1741096668832277847"
    exit -1
fi

# remove existing qdiscs
sudo tc qdisc del root dev ${EMULATOR_IFACE_LEFT}
sudo tc qdisc del root dev ${EMULATOR_IFACE_RIGHT} 


IFS=' '
read -r -a lossparams <<< "$LOSS_PARAMS"

DELAY=$(echo "$RTT/2" | bc)
MAX_BURST=$(echo "scale=0; $RATE*1000000/1000" | bc)
LIMIT=100000

sudo tc qdisc add dev ${EMULATOR_IFACE_LEFT} root handle 1: tbf rate ${RATE}mbit limit ${BUFFER_SIZE} burst ${MAX_BURST}
sudo tc qdisc add dev ${EMULATOR_IFACE_RIGHT} root handle 1: tbf rate ${RATE}mbit limit ${BUFFER_SIZE} burst ${MAX_BURST}


TRY_SEED=""
if iproute2_seed_support; then
TRY_SEED="seed $SEED"
fi

if [[ $LOSS_MODE = "random" ]]; then
    sudo tc qdisc add dev ${EMULATOR_IFACE_LEFT} parent 1: handle 10: netem delay ${DELAY}ms limit ${LIMIT} loss random ${lossparams[0]}% $TRY_SEED
    sudo tc qdisc add dev ${EMULATOR_IFACE_RIGHT} parent 1: handle 10: netem delay ${DELAY}ms limit ${LIMIT}
elif [[ $LOSS_MODE = "gemodel" ]]; then
    if [[ ${#lossparams[@]} != 4 ]]; then
      echo "!! gemodel loss: missing parameters"
      exit -1
    fi
    sudo tc qdisc add dev ${EMULATOR_IFACE_LEFT} parent 1: handle 10: netem delay ${DELAY}ms limit ${LIMIT} loss gemodel ${lossparams[0]}% ${lossparams[1]}% ${lossparams[2]}% ${lossparams[3]}% $TRY_SEED
    sudo tc qdisc add dev ${EMULATOR_IFACE_RIGHT} parent 1: handle 10: netem delay ${DELAY}ms limit ${LIMIT}
else 
    sudo tc qdisc add dev ${EMULATOR_IFACE_LEFT} parent 1: handle 10: netem delay ${DELAY}ms limit ${LIMIT}
    sudo tc qdisc add dev ${EMULATOR_IFACE_RIGHT} parent 1: handle 10: netem delay ${DELAY}ms limit ${LIMIT}
fi

sudo tc qdisc show dev ${EMULATOR_IFACE_LEFT}
sudo tc qdisc show dev ${EMULATOR_IFACE_RIGHT}
