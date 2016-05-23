from collections import namedtuple
from enum import Enum

# Source: http://wiki.kerbalspaceprogram.com/wiki/Parts

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
    NuclearPropulsion = 71      # depends on HeavierRocketry
    VeryHeavyRocketry = 81      # depends on HeavierRocketry or LargeVolumeContainment
    HyperSonicFlight = 82       # depends on Aerodynamics
    IonPropulsion = 83          # depends on ScienceTech and UnmannedTech
    AerospaceTech = 91          # depends on HypersonicFlight

    def DependsOn(self, a):
        # TODO: redo this, implementing engineering stuff and knowing about the tree
        if self is a:
            return True
        if  (self is ResearchNode.VeryHeavyRocketry) or \
            (self is ResearchNode.HyperSonicFlight) or \
            (self is ResearchNode.AerospaceTech) or \
            (self is ResearchNode.IonPropulsion):
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

    def MoreSophisticated(self, a):
        return (self is not a and a.DependsOn(self))

LiquidFuelEngine = namedtuple('LiquidFuelEngine', ['size', 'name', 'cost', 'm', 'isp_atm', 'isp_vac', 'F_vac', 'tvc', 'level'])

LiquidFuelEngines = [
        LiquidFuelEngine(RadialSize.RdMntd,'LV-1R Spider',   120,  20,   260, 290, 2000,   8, ResearchNode.PrecisionPropulsion),
        LiquidFuelEngine(RadialSize.RdMntd,'24-77 Twitch',   400,  90,   250, 290, 16000,  8, ResearchNode.PrecisionPropulsion),
        LiquidFuelEngine(RadialSize.RdMntd,'Mk-55 Thud',     820,  900,  275, 305, 120000, 8, ResearchNode.AdvancedRocketry),
        LiquidFuelEngine(RadialSize.Tiny,  'LV-1 Ant',       110,  20,   80,  315, 2000,   0, ResearchNode.PropulsionSystems),
        LiquidFuelEngine(RadialSize.Tiny,  '48-7S Spark',    200,  100,  270, 300, 18000,  3, ResearchNode.PropulsionSystems),
        LiquidFuelEngine(RadialSize.Small, 'LV-909 Terrier', 390,  500,  85,  345, 60000,  4, ResearchNode.AdvancedRocketry),
        LiquidFuelEngine(RadialSize.Small, 'LV-T30 Reliant', 1100, 1250, 280, 300, 215000, 0, ResearchNode.BasicRocketry),
        LiquidFuelEngine(RadialSize.Small, 'LV-T45 Swivel',  1200, 1500, 270, 320, 200000, 3, ResearchNode.GeneralRocketry),
        LiquidFuelEngine(RadialSize.Small, 'S3 KS-25 Vector',18000,4000, 295, 315, 1000000,10.5,ResearchNode.VeryHeavyRocketry),
        LiquidFuelEngine(RadialSize.Small, 'CR7 RAPIER',     6000, 2000, 275, 305, 180000, 3, ResearchNode.AerospaceTech),
        LiquidFuelEngine(RadialSize.Small, 'T-1 Dart',       3850, 1000, 290, 340, 180000, 0, ResearchNode.HyperSonicFlight),
        LiquidFuelEngine(RadialSize.Large, 'RE-L10 Poodle',  1300, 1750, 90,  350, 250000, 4.5,ResearchNode.HeavyRocketry),
        LiquidFuelEngine(RadialSize.Large, 'RE-I5 Skipper',  5300, 3000, 280, 320, 650000, 2, ResearchNode.HeavyRocketry),
        LiquidFuelEngine(RadialSize.Large, 'RE-M3 Mainsail', 13000,6000, 285, 320, 1500000,2, ResearchNode.HeavierRocketry),
        LiquidFuelEngine(RadialSize.Large, 'LFB Twin-Boar',  11250,6500, 280, 300, 2000000,1.5,ResearchNode.HeavierRocketry),
        LiquidFuelEngine(RadialSize.ExtraLarge, 'KR-2L+ Rhino', 25000,9000, 255, 340, 2000000,4,ResearchNode.VeryHeavyRocketry),
        LiquidFuelEngine(RadialSize.ExtraLarge, 'KS-25x4 Mammoth', 39000,15000, 295, 315, 4000000,2,ResearchNode.VeryHeavyRocketry) ]

# Twin-Boar is the engine as listed above, with forced addition of the 36 ton large liquid fuel tank.

# liquid fuel tank quantities.
# empty weight is 1/9 of full weight.
# content is 0.9 parts liquid fuel and 1.1 parts oxidizer.

FuelTank = namedtuple('FuelTank', ['size', 'cost', 'm_full'])

# TODO: support adapter tanks

RocketFuelTanks = [
        FuelTank(RadialSize.Tiny, 70, 225),               # 0
        FuelTank(RadialSize.Small, 150, 562.5),           # 1
        FuelTank(RadialSize.Small, 275, 1125),
        FuelTank(RadialSize.Small, 500, 2250),
        FuelTank(RadialSize.Small, 800, 4500),            # 4
        FuelTank(RadialSize.Large, 800, 4500),            # 5
        FuelTank(RadialSize.Large, 1550, 9000),
        FuelTank(RadialSize.Large, 3000, 18000),
        FuelTank(RadialSize.Large, 5750, 36000),          # 8
        FuelTank(RadialSize.ExtraLarge, 3250, 20250),     # 9
        FuelTank(RadialSize.ExtraLarge, 6500, 40500),
        FuelTank(RadialSize.ExtraLarge, 13000, 81000) ]   # 11

SmallestTank = { RadialSize.Tiny : 0, RadialSize.Small: 1, RadialSize.Large: 5, RadialSize.ExtraLarge: 9 }
BiggestTank =  { RadialSize.Tiny : 0, RadialSize.Small: 4, RadialSize.Large: 8, RadialSize.ExtraLarge: 11 }

SpecialEngine = namedtuple('SpecialEngine', ['size', 'name', 'cost', 'm', 'isp_atm', 'isp_vac', 'F_vac', 'tvc', 'level', 'f_e'])
# TODO: overthink this. f_e is a property of the tank, not of the engine.

AtomicRocketMotor = SpecialEngine(RadialSize.Small, 'LV-N Nerv Atomic Rocket Motor', 10000, 3000, 185, 800, 60000, 0, ResearchNode.NuclearPropulsion, 5/18)
AtomicTankFactor = 23/45    # Mass of full atomic fuel tank / Mass of full liquid fuel tank

# TODO. Currently we only support PB-X150 Xenon Container. We should think about
# alternative designs using the ion engine. Especially considering radially
# mounted tanks would be easy to implement
ElectricPropulsionSystem = SpecialEngine(RadialSize.Tiny, 'IX-6315 Dawn Electric Propulsion System', 8000, 250, 100, 4200, 2000, 0, ResearchNode.IonPropulsion, 5/7)
XenonTank = FuelTank(RadialSize.Tiny, 3000, 120)    # TODO: double check validity of this data.
XenonUnitMass = 0.1

SolidFuelBooster = namedtuple('SolidFuelBooster', ['name', 'cost', 'm_full', 'm_empty', 'isp_atm', 'isp_vac', 'F_vac', 'level'])

SolidFuelBoosters = [
        SolidFuelBooster('RT-5 Flea',    200,  1500,  450,  140, 165, 192000, ResearchNode.Start),
        SolidFuelBooster('RT-10 Hammer', 400,  3560,  750,  170, 195, 227000, ResearchNode.BasicRocketry),
        SolidFuelBooster('BACC Thumper', 850,  7650,  1500, 175, 210, 300000, ResearchNode.GeneralRocketry),
        SolidFuelBooster('S1 Kickback',  2700, 24000, 4500, 195, 220, 670000, ResearchNode.HeavyRocketry) ]

# Extra for stacked stage
StackstageExtraMass = 50
StackstageExtraCost = 400
StackstageExtraNote = "TR-18A Stack Decoupler"

# Extra for radial stage
# TODO: overthink this (maybe make it adjustable)
# This is a very heavy but safe default setting, also having the effect of
# reducing the count of extra radial solid fuel boosters.
RadialstageExtraMass = 50 + 75 + 2*50
RadialstageExtraCost = 700 + 320 + 2*42
RadialstageExtraNote = "TT-70 Radial Decoupler, Advanced Nose Cone, 2 * EAS-4 Strut Connector"
