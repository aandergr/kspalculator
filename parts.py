from collections import namedtuple
from enum import Enum

class RadialSize(Enum):
    Tiny = 1
    Small = 2
    Large = 3
    ExtraLarge = 4
    RadialMounted = 9

# TODO: Add adapters, solid fuel boosters, etc.

LiquidFuelEngine = namedtuple('LiquidFuelEngine', ['size', 'name', 'cost', 'm', 'isp_atm', 'isp_vac', 'F_atm', 'F_vac'])
# TODO: add more parameters to optimize for

# TODO: support radially mounted engines
# TODO: support monopropellant engines
# TODO: support ion engines
# TODO: support atomic engines
# TODO: support engines which have tank included

LiquidFuelEngines = [
        LiquidFuelEngine(RadialSize.Tiny,  'LV-1 Ant',       110,  20,   80,  315, 510,    2000),
        LiquidFuelEngine(RadialSize.Tiny,  '48-7S Spark',    200,  100,  270, 300, 16200,  18000),
        LiquidFuelEngine(RadialSize.Small, 'LV-909 Terrier', 390,  500,  85,  345, 14783,  60000),
        LiquidFuelEngine(RadialSize.Small, 'LV-T30 Reliant', 1100, 1250, 280, 300, 200670, 215000),
        LiquidFuelEngine(RadialSize.Small, 'LV-T45 Swivel',  1200, 1500, 270, 320, 168750, 200000),
        LiquidFuelEngine(RadialSize.Small, 'S3 KS-25 Vector',18000,4000, 295, 315, 936500, 1000000),
        LiquidFuelEngine(RadialSize.Small, 'CR7 RAPIER',     6000, 2000, 275, 305, 162300, 180000),
        LiquidFuelEngine(RadialSize.Small, 'T-1 Dart',       3850, 1000, 290, 340, 153530, 180000),
        LiquidFuelEngine(RadialSize.Large, 'RE-L10 Poodle',  1300, 1750, 90,  350, 64290,  250000),
        LiquidFuelEngine(RadialSize.Large, 'RE-I5 Skipper',  5300, 3000, 280, 320, 568750, 650000),
        LiquidFuelEngine(RadialSize.Large, 'RE-M3 Mainsail', 13000,6000, 285, 320, 1379000,1500000),
        LiquidFuelEngine(RadialSize.ExtraLarge, 'KR-2L+ Rhino', 25000,9000, 255, 340, 1500000,2000000),
        LiquidFuelEngine(RadialSize.ExtraLarge, 'KS-25x4 Mammoth', 39000,15000, 295, 315, 3746000,4000000) ]


# liquid fuel tank quantities.
# empty weight is 1/9 of full weight.
# content is 0.9 parts liquid fuel and 1.1 parts oxidizer.

RocketFuelTank = namedtuple('RocketFuelTank', ['size', 'cost', 'm_full'])

RocketFuelTanks = [
        RocketFuelTank(RadialSize.Tiny, 70, 225),               # 0
        RocketFuelTank(RadialSize.Small, 150, 562.5),           # 1
        RocketFuelTank(RadialSize.Small, 275, 1125),
        RocketFuelTank(RadialSize.Small, 500, 2250),
        RocketFuelTank(RadialSize.Small, 800, 4500),            # 4
        RocketFuelTank(RadialSize.Large, 800, 4500),            # 5
        RocketFuelTank(RadialSize.Large, 1550, 9000),
        RocketFuelTank(RadialSize.Large, 3000, 18000),
        RocketFuelTank(RadialSize.Large, 5750, 36000),          # 8
        RocketFuelTank(RadialSize.ExtraLarge, 3250, 20250),     # 9
        RocketFuelTank(RadialSize.ExtraLarge, 6500, 40500),
        RocketFuelTank(RadialSize.ExtraLarge, 13000, 81000) ]   # 11

SmallestTank = { RadialSize.Tiny : 0, RadialSize.Small: 1, RadialSize.Large: 5, RadialSize.ExtraLarge: 9 }
BiggestTank =  { RadialSize.Tiny : 0, RadialSize.Small: 4, RadialSize.Large: 8, RadialSize.ExtraLarge: 11 }

