#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser, ArgumentTypeError, SUPPRESS
from textwrap import fill

from parts import kspversion
from bodies import CelestialBody, Location, CalculateCost

version = '0.9'

def nonnegative_float(value):
    fl = float(value)
    if fl < 0.0:
        raise ArgumentTypeError("%r is negative" % value)
    return fl


def positive_float(value):
    fl = float(value)
    if fl <= 0.0:
        raise ArgumentTypeError("%r is not positive" % value)
    return fl


def normalize_body_locations(values):
    """Verifies that the given list of values contains valid body.location pairs."""

    def Normalize(pair):
        body_and_location = pair.split('.')
        if len(body_and_location) != 2:
            raise ArgumentTypeError("%r is not of the form body.location" % pair)

        body, location = body_and_location
        body = body.capitalize()
        location = location.capitalize()
        if not body in CelestialBody.__members__.keys():
            raise ArgumentTypeError("%s is not a valid celestial body" % body)
        if not location in Location.__members__.keys():
            raise ArgumentTypeError("%s is not a valid location" % location)
        return "%s.%s" % (body, location)

    return "%s-%s" % (Normalize(values[0]), Normalize(values[1]))


def dvtuple(value):
    body_locations = value.split('-')
    if len(body_locations) == 2:
        return normalize_body_locations(body_locations)

    s = value.split(':')
    positive_float(s[0])
    if len(s) > 1:
        nonnegative_float(s[1])
    if len(s) > 2:
        nonnegative_float(s[2])
    if len(s) > 3:
        raise ArgumentTypeError("%r contains too many ':'s" % value)
    return value


epilog = "For a more detailed explanation on how to use this tool, please consider reading " \
        "README.md file.  If you encounter any issues, do not hesitate to report them at "\
        "https://github.com/aandergr/kspalculator/issues."

bodies = ', '.join(sorted([b.name.lower() for b in CelestialBody]))
locations = ', '.join(sorted([l.name.lower() for l in Location]))

parser = ArgumentParser(description='Determine best rocket design for given constraints',
        epilog=epilog)
parser.add_argument('payload', type=nonnegative_float, help='Payload in kg')
parser.add_argument('dvtuples', type=dvtuple,
                    metavar='deltav[:min_acceleration[:pressure]] or body.location', nargs='+',
        help='One or more tuples of required delta v (in m/s), minimum acceleration (in m/s²) and '
             'environment pressure (0.0 = vacuum, 1.0 = ATM) at each flight phase. Default for '
             'minimum acceleration is 0 m/s², default for pressure is vacuum. Alternatively, '
             'phases may be given as "body.location-body.location" pairs where valid body values '
             'are: ' + bodies + ' and locations are: ' + locations + '. e.g., '
             'a stage from Kerbin orbit to Minmus surface would be kerbin.orbit-minmus.surface')
parser.add_argument('-V', '--version', action='version',
        version=('kspalculator version %s, for KSP version %s.' % (version, kspversion)))
parser.add_argument('-q', '--quiet', action='store_true', help='Do not print prologue')
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
parser.add_argument('-g', '--gimbal', action='count', default=0,
        help='If specified once, prefer engines with gimbal (aka thrust vectoring) over engines '
        'without gimbal. If specified twice (i.e. -gg), also consider gimbal range and prefer '
        'engines with better thrust vectoring angle.')
parser.add_argument('--show-all-solutions', action='store_true', help=SUPPRESS)

args = parser.parse_args()

# we have the import here (instead of above) to have short execution time in
# case of calling with e.g. '-h' only.
from finder import Finder
from parts import RadialSize


def _ParseBodyLocationPair(pair):
    start_body, start_location = pair[0].split('.')
    end_body, end_location = pair[1].split('.')

    start_body = CelestialBody.__members__[start_body]
    start_location = Location.__members__[start_location]
    end_body = CelestialBody.__members__[end_body]
    end_location = Location.__members__[end_location]

    return CalculateCost(start_body, start_location, end_body, end_location)


def _ParseDVParam(str_value):
    body_locations = str_value.split('-')
    if len(body_locations) == 2:
        return _ParseBodyLocationPair(body_locations)

    s = str_value.split(':')
    deltav = float(s[0])
    acceleration = 0.0 if len(s) < 2 else float(s[1])
    pressure = 0.0 if len(s) < 3 else float(s[2])
    return [deltav], [acceleration], [pressure]


preferred_size = None
if args.preferred_radius is not None:
    if args.preferred_radius == "tiny":
        preferred_size = RadialSize.Tiny
    elif args.preferred_radius == "small":
        preferred_size = RadialSize.Small
    elif args.preferred_radius == "large":
        preferred_size = RadialSize.Large
    else:
        preferred_size = RadialSize.ExtraLarge

dv = []
ac = []
pr = []
for st in args.dvtuples:
    deltavs, accelerations, pressures = _ParseDVParam(st)
    dv.extend(deltavs)
    ac.extend(accelerations)
    pr.extend(pressures)

finder = Finder(args.payload, preferred_size, dv, ac, pr, args.gimbal, args.boosters,
                args.electricity, args.length)
D = finder.Find(not args.show_all_solutions, args.cheapest)

if not args.quiet:
    print(fill("Printing the best (and only the best!) designs (i.e. engine and tank combinations) "
        "fulfilling these requirements:"))
    print("- Payload: %.0f kg." % args.payload)
    print("- Flight phases: ", end='')
    for i in range(len(dv)):
        print("%.0f m/s, %.1f m/s², %.2f atm%s" %
                (dv[i], ac[i], pr[i], "; " if i != len(dv)-1 else "."), end='')
    print() # newline
    print("- Preferred size: %s." % args.preferred_radius)
    if args.gimbal == 0:
        print("- You do not need engine with thrust vectoring.")
    elif args.gimbal == 1:
        print("- You prefer engines with thrust vectoring.")
    else:
        print("- You prefer engines with the best thrust vectoring.")
    if not args.boosters:
        print("- Solid fuel boosters must not be added to the ship.")
    if not args.electricity:
        print("- You do not need engine generating electric power.")
    if not args.length:
        print("- You do not care about length of engine.")
    print(fill("Note that these options heavily influence which engine choices are shown to you. "
        "If these aren't your constraints, consult kspalculator.py --help and try again."))
    print()

for d in D:
    d.PrintInfo()
    print("")

if not args.quiet and len(D) == 0:
    print("Sorry, nothing found. Change constraints and try again.")
