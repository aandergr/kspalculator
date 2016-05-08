from collections import namedtuple
from enum import Enum

class RadialSize(Enum):
    Tiny = 1
    Small = 2
    Large = 3
    ExtraLarge = 4
    RdMntd = 9      # radially mounted

class ResearchNode(Enum):
    # only relevant nodes yet
    Start = 11
    BasicRocketry = 21
    GeneralRocketry = 31
    AdvancedRocketry = 41
    HeavyRocketry = 51
    PropulsionSystems = 52
    HeavierRocketry = 61        # depends on HeavyRocketry
    PrecisionPropulsion = 62    # depends on PropulsionSystems
    VeryHeavyRocketry = 81      # depends on HeavierRocketry or LargeVolumeContainment
    HyperSonicFlight = 82       # depends on Aerodynamics
    AerospaceTech = 91          # depends on HypersonicFlight

    def DependsOn(self, a):
        if self is a:
            return True
        if  (self is ResearchNode.VeryHeavyRocketry) or \
            (self is ResearchNode.HyperSonicFlight) or \
            (self is ResearchNode.AerospaceTech):
            # interestingly, these nodes can be reached without having
            # researched the other *Rocketry technologies.
            if a is ResearchNode.Start:
                return True
            else:
                return False
        if self is ResearchNode.PrecisionPropulsion:
            if a is ResearchNode.PropulsionSystems or a.value <= 41:
                return True
            else:
                return False
        return a.value+10 <= self.value

# TODO: Add adapters, solid fuel boosters, etc.

LiquidFuelEngine = namedtuple('LiquidFuelEngine', ['size', 'name', 'cost', 'm', 'isp_atm', 'isp_vac', 'F_atm', 'F_vac', 'tvc', 'level'])

# TODO: support radially mounted engines
# TODO: support monopropellant engines
# TODO: support ion engines
# TODO: support atomic engines
# TODO: support engines which have tank included

LiquidFuelEngines = [
        LiquidFuelEngine(RadialSize.RdMntd,'LV-1R Spider',   120,  20,   260, 290, 1793,   2000,   8, ResearchNode.PrecisionPropulsion),
        LiquidFuelEngine(RadialSize.RdMntd,'24-77 Twitch',   400,  90,   250, 290, 13793,  16000,  8, ResearchNode.PrecisionPropulsion),
        LiquidFuelEngine(RadialSize.RdMntd,'Mk-55 Thud',     820,  900,  275, 305, 108200, 120000, 8, ResearchNode.AdvancedRocketry),
        LiquidFuelEngine(RadialSize.Tiny,  'LV-1 Ant',       110,  20,   80,  315, 510,    2000,   0, ResearchNode.PropulsionSystems),
        LiquidFuelEngine(RadialSize.Tiny,  '48-7S Spark',    200,  100,  270, 300, 16200,  18000,  3, ResearchNode.PropulsionSystems),
        LiquidFuelEngine(RadialSize.Small, 'LV-909 Terrier', 390,  500,  85,  345, 14783,  60000,  4, ResearchNode.AdvancedRocketry),
        LiquidFuelEngine(RadialSize.Small, 'LV-T30 Reliant', 1100, 1250, 280, 300, 200670, 215000, 0, ResearchNode.BasicRocketry),
        LiquidFuelEngine(RadialSize.Small, 'LV-T45 Swivel',  1200, 1500, 270, 320, 168750, 200000, 3, ResearchNode.GeneralRocketry),
        LiquidFuelEngine(RadialSize.Small, 'S3 KS-25 Vector',18000,4000, 295, 315, 936500, 1000000,10.5,ResearchNode.VeryHeavyRocketry),
        LiquidFuelEngine(RadialSize.Small, 'CR7 RAPIER',     6000, 2000, 275, 305, 162300, 180000, 3, ResearchNode.AerospaceTech),
        LiquidFuelEngine(RadialSize.Small, 'T-1 Dart',       3850, 1000, 290, 340, 153530, 180000, 0, ResearchNode.HyperSonicFlight),
        LiquidFuelEngine(RadialSize.Large, 'RE-L10 Poodle',  1300, 1750, 90,  350, 64290,  250000, 4.5,ResearchNode.HeavyRocketry),
        LiquidFuelEngine(RadialSize.Large, 'RE-I5 Skipper',  5300, 3000, 280, 320, 568750, 650000, 2, ResearchNode.HeavyRocketry),
        LiquidFuelEngine(RadialSize.Large, 'RE-M3 Mainsail', 13000,6000, 285, 320, 1379000,1500000,2, ResearchNode.HeavierRocketry),
        LiquidFuelEngine(RadialSize.ExtraLarge, 'KR-2L+ Rhino', 25000,9000, 255, 340, 1500000,2000000,4,ResearchNode.VeryHeavyRocketry),
        LiquidFuelEngine(RadialSize.ExtraLarge, 'KS-25x4 Mammoth', 39000,15000, 295, 315, 3746000,4000000,2,ResearchNode.VeryHeavyRocketry) ]


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

