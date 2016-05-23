#!/usr/bin/env python3

from argparse import ArgumentParser, SUPPRESS
from parts import kspversion

version = '0.9-rc'

epilog = """
deltav:pressure tuples:
You specify which delta-v (in m/s) at which pressure (0.0 = vacuum, 1.0 = ATM)
your ship must be able to reach. You might specify more than one of these
tuples. This might be useful if you're going to fly through different
environments, e.g. starting in atmosphere and later flying through vacuum.
A safe kerbin launch is "905:13:1.0 3650:13:0.18".
"""

parser = ArgumentParser(description='Determine best rocket design for given constraints',
        epilog=epilog)
parser.add_argument('payload', type=float, help='Payload in kg')
parser.add_argument('dvtuples', metavar='deltav[:min_acceleration[:pressure]]', nargs='+',
        help='Tuples of required delta v, minimum acceleration and environment pressure at each '
        'flight phase. Defaults for minimum acceleration is 0 m/s² and for '
        'pressure 0 ATM (= vacuum)')
parser.add_argument('-V', '--version', action='version',
        version=('kspalculator version %s, for KSP version %s.' % (version, kspversion)))
parser.add_argument('-c', '--cheapest', action='store_true',
        help='Sort by cost instead of weight')
parser.add_argument('-b', '--boosters', action='store_true',
        help='Consider designs with solid fuel boosters')
parser.add_argument('-R', '--preferred-radius', choices=['tiny', 'small', 'large', 'extralarge'],
        type = str.lower, help='Preferred radius of the stage. Tiny = 0.625 m, Small = 1.25 m, '
        'Large = 2.5 m (Rockomax), ExtraLarge = 3.75 m (Kerbodyne).')
parser.add_argument('-e', '--electricity', action='store_true',
        help='Consider engines generating electricity advantageous. This means, designs using '
        'electricity generating engines are presented even if they are worse by other criteria.')
parser.add_argument('-l', '--length', '--lander', action='store_true',
        help='Prefer short (or radially mounted) engines, as might be needed for building a lander')
parser.add_argument('-g', '--gimbal', action='count',
        help='If specified once, prefer engines with gimbal (aka thrust vectoring) over engines '
        'without gimbal. If specified twice (i.e. -gg), also consider gimbal range and prefer '
        'engines with better thrust vectoring angle.')
parser.add_argument('--show-all-solutions', action='store_true', help=SUPPRESS)

args = parser.parse_args()

# we have the import here (instead of above) to have short execution time in
# case of calling with e.g. '-h' only.
from design import FindDesigns
from parts import RadialSize

ps = None
if args.preferred_radius is not None:
    if args.preferred_radius == "tiny":
        ps = RadialSize.Tiny
    elif args.preferred_radius == "small":
        ps = RadialSize.Small
    elif args.preferred_radius == "large":
        ps = RadialSize.Large
    else:
        ps = RadialSize.ExtraLarge

dv = []
ac = []
pr = []
for st in args.dvtuples:
    s = st.split(':')
    dv.append(float(s[0]))
    ac.append(0.0 if len(s) < 2 else float(s[1]))
    pr.append(0.0 if len(s) < 3 else float(s[2]))

if args.gimbal is None:
    args.gimbal = 0

all_designs = FindDesigns(args.payload, pr, dv, ac, ps,
        args.gimbal, args.boosters, args.electricity, args.length)

if args.show_all_solutions:
    D = all_designs
else:
    D = [d for d in all_designs if d.IsBest]

if args.cheapest:
    D = sorted(D, key=lambda dsg: dsg.cost)
else:
    D = sorted(D, key=lambda dsg: dsg.mass)

for d in D:
    d.PrintInfo()
    print("")
