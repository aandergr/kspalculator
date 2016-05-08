#!/usr/bin/env python3

from argparse import ArgumentParser

parser = ArgumentParser(description='Determine best rocket design')
parser.add_argument('payload', type=float, help='Payload in kg')
parser.add_argument('deltav', type=float, help='Required Delta-V in m/s')
parser.add_argument('acceleration', type=float, help='Required minimum acceleration')
parser.add_argument('pressure', type=float, help='Air pressure, 0.0 = vacuum, 1.0 = kerbin surface')
parser.add_argument('-c', '--cheapest', action='store_true', help='Sort by cost instead of weight')
parser.add_argument('--keep', action='store_true', help='Do not hide bad solutions')

args = parser.parse_args()

# we have the import here to have short execution time in case of calling with
# e.g. '-h' only.
from design import FindDesigns

all_designs = FindDesigns(args.payload, args.pressure, args.deltav, args.acceleration)

if args.keep:
    D = all_designs
else:
    D = [d for d in all_designs if d.IsBest]

if args.cheapest:
    D = sorted(D, key=lambda dsg: dsg.cost)
else:
    D = sorted(D, key=lambda dsg: dsg.mass)

for d in D:
    d.printinfo()
    print("")
