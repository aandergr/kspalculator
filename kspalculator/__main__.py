#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError, SUPPRESS
from textwrap import fill

from .finder import Finder
from .parts import RadialSize, kspversion
from . import __version__ as get_version
from . import __doc__ as summary

def nonnegative_float(string):
    fl = float(string)
    if fl < 0.0:
        raise ArgumentTypeError("%r is negative" % string)
    return fl

def positive_float(string):
    fl = float(string)
    if fl <= 0.0:
        raise ArgumentTypeError("%r is not positive" % string)
    return fl

def dvtuple(string):
    spl = string.split(':')
    positive_float(spl[0])
    if len(spl) > 1:
        nonnegative_float(spl[1])
    if len(spl) > 2:
        nonnegative_float(spl[2])
    if len(spl) > 3:
        raise ArgumentTypeError("%r contains too many ':'" % string)
    return string

def main():
    # pylint:disable=too-many-statements

    epilog = "If you encounter any issues, do not hesitate to report them at "\
            "https://github.com/aandergr/kspalculator/issues."

    parser = ArgumentParser(description=summary, epilog=epilog)
    parser.add_argument('payload', type=nonnegative_float, help='Payload in kg')
    parser.add_argument('dvtuples', type=dvtuple, metavar='deltav[:min_acceleration[:pressure]]', nargs='+',
            help='Tuples of required delta v (in m/s), minimum acceleration (in m/s²) and environment '
            'pressure (0.0 = vacuum, 1.0 = ATM) at each flight phase. Default for minimum acceleration '
            'is 0 m/s², default for pressure is vacuum.')
    parser.add_argument('-V', '--version', action='version',
            version=('kspalculator version %s, for KSP version %s.' % (get_version(), kspversion)))
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
    parser.add_argument('-m', '-r', '--monopropellant', '--rcs', action='store_true',
            help='Prefer engines using monopropellant (RCS fuel)')
    parser.add_argument('--show-all-solutions', action='store_true', help=SUPPRESS)

    args = parser.parse_args()

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
        s = st.split(':')
        dv.append(float(s[0]))
        ac.append(0.0 if len(s) < 2 else float(s[1]))
        pr.append(0.0 if len(s) < 3 else float(s[2]))

    finder = Finder(args.payload, preferred_size, dv, ac, pr, args.gimbal, args.boosters,
                    args.electricity, args.length, args.monopropellant)
    D = finder.find(not args.show_all_solutions, args.cheapest)

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
        if args.monopropellant:
            print("- You prefer engines using monopropellant.")
        for warning in finder.lint():
            print(fill("WARNING: "+warning))
        print(fill("Note that these options heavily influence which engine choices are shown to you. "
            "If these aren't your constraints, consult kspalculator.py --help and try again."))
        print()

    for d in D:
        print(d)

    if not args.quiet and len(D) == 0:
        print("Sorry, nothing found. Change constraints and try again.")

if __name__ == '__main__':
    main()
