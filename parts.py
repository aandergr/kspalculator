from collections import namedtuple
from enum import Enum

class RadialSize(Enum):
    Tiny = 1
    Small = 2
    Large = 3
    ExtraLarge = 4
    RadialMounted = 9

# TODO: Add adapters, solid fuel boosters, radial engines, other engine types, etc.

LiquidFuelEngine = namedtuple('LiquidFuelEngine', ['size', 'name', 'cost', 'm', 'isp_atm', 'isp_vac', 'F_atm', 'F_vac'])
# TODO: add more parameters to optimize for

# TODO: fill table
LiquidFuelEngines = [
        LiquidFuelEngine(RadialSize.Small, 'LV-909 Terrier', 390,  500,  85,  345, 14783,  60000),
        LiquidFuelEngine(RadialSize.Small, 'LV-T30 Reliant', 1100, 1250, 280, 300, 200670, 215000) ]

# liquid fuel tank quantities.
# empty weight is 1/9 of full weight.
# content is 0.9 parts liquid fuel and 1.1 parts oxidizer.

RocketFuelTank = namedtuple('RocketFuelTank', ['size', 'cost', 'm_full'])

# TODO: fill table
RocketFuelTanks = [
        RocketFuelTank(RadialSize.Small, 150, 562.5),
        RocketFuelTank(RadialSize.Small, 275, 1125),
        RocketFuelTank(RadialSize.Small, 500, 2250),
        RocketFuelTank(RadialSize.Small, 800, 4500) ]

Small_SmallestTank = 0
Small_BiggestTank = 3
