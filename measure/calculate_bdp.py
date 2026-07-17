import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rate", required=True, type=int)
parser.add_argument("--rtt", required=True, type=int)
parser.add_argument("--factor", required=True, type=float)

args = parser.parse_args()

rate_mbit = args.rate
rtt_ms = args.rtt

rate_bit_s = float(rate_mbit * 1000000)
rate_byte_s = rate_bit_s / 8
rtt_s = float(rtt_ms / 1000)
bdp = int(rate_byte_s * rtt_s * args.factor)
print(bdp)

