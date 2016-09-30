# -*- coding: utf-8 -*-
# Python 2.7 support.
from __future__ import division
from enum import Enum

from collections import namedtuple

from .techtree import Node as ResearchNode

# Source: http://wiki.kerbalspaceprogram.com/wiki/Parts, as well as in-game info

kspversion = '1.1.3'

class RadialSize(Enum):
    Tiny = 1
    Small = 2
    Large = 3
    ExtraLarge = 4
    RadiallyMounted = 9      # radially mounted

# A note about length of engine: We have this option, because for landers with landing legs, short
# engines are an advantage. So which height an engine has, depends on the compatibility with landing
# struts, ordered by their mass. We have this data from KSP wiki. Unfortunately, the listings there
# are not comprehensive.
#  0 -> ok with LT-05 µ landing strut (all radially mounted, Terrier, Spark, Ant)
#  1 -> ok with LT-1 landing struts (Dart)
#  2 -> ok with LT-2 landing struts (Poodle, Reliant, Swivel)
#  3 -> all others...

Engine = namedtuple('Engine', ['size', 'name', 'cost', 'm', 'isp_atm',
    'isp_vac', 'F_vac', 'tvc', 'level', 'electricity', 'length'])

LiquidFuelEngines = [
        Engine(RadialSize.RadiallyMounted, 'LV-1R Spider', 120, 20, 260, 290, 2000, 8,
            ResearchNode.PrecisionPropulsion, 0, 0),
        Engine(RadialSize.RadiallyMounted, '24-77 Twitch', 400, 90, 250, 290, 16000, 8,
            ResearchNode.PrecisionPropulsion, 0, 0),
        Engine(RadialSize.RadiallyMounted, 'Mk-55 Thud', 820, 900, 275, 305, 120000, 8,
            ResearchNode.AdvancedRocketry, 0, 0),
        Engine(RadialSize.Tiny,  'LV-1 Ant',       110,  20,   80,  315, 2000,   0,
            ResearchNode.PropulsionSystems, 0, 0),
        Engine(RadialSize.Tiny,  '48-7S Spark',    200,  100,  270, 300, 18000,  3,
            ResearchNode.PropulsionSystems, 0, 0),
        Engine(RadialSize.Small, 'LV-909 Terrier', 390,  500,  85,  345, 60000,  4,
            ResearchNode.AdvancedRocketry, 0, 0),
        Engine(RadialSize.Small, 'LV-T30 Reliant', 1100, 1250, 280, 300, 215000, 0,
            ResearchNode.GeneralRocketry, 1, 2),
        Engine(RadialSize.Small, 'LV-T45 Swivel',  1200, 1500, 270, 320, 200000, 3,
            ResearchNode.BasicRocketry, 1, 2),
        Engine(RadialSize.Small, 'S3 KS-25 Vector',18000,4000, 295, 315, 1000000, 10.5,
            ResearchNode.VeryHeavyRocketry, 1, 3),
        Engine(RadialSize.Small, 'CR7 RAPIER',     6000, 2000, 275, 305, 180000, 3,
            ResearchNode.AerospaceTech, 0, 3),
        Engine(RadialSize.Small, 'T-1 Dart',       3850, 1000, 290, 340, 180000, 0,
            ResearchNode.HypersonicFlight, 1, 1),
        Engine(RadialSize.Large, 'RE-L10 Poodle',  1300, 1750, 90,  350, 250000, 4.5,
            ResearchNode.HeavyRocketry, 1, 2),
        Engine(RadialSize.Large, 'RE-I5 Skipper',  5300, 3000, 280, 320, 650000, 2,
            ResearchNode.HeavyRocketry, 1, 3),
        Engine(RadialSize.Large, 'RE-M3 Mainsail', 13000,6000, 285, 310, 1500000,2,
            ResearchNode.HeavierRocketry, 1, 3),
        Engine(RadialSize.Large, 'LFB Twin-Boar',  11250,6500, 280, 300, 2000000, 1.5,
            ResearchNode.HeavierRocketry, 0, 3),
        Engine(RadialSize.ExtraLarge, 'KR-2L+ Rhino', 25000,9000, 255, 340, 2000000, 4,
            ResearchNode.VeryHeavyRocketry, 1, 3),
        Engine(RadialSize.ExtraLarge, 'KS-25x4 Mammoth', 39000,15000, 295, 315, 4000000, 2,
            ResearchNode.VeryHeavyRocketry, 1, 3) ]

# Twin-Boar is the engine as listed above, with forced addition of the 36 ton large liquid fuel
# tank (TwinBoarPseudoTank)

# liquid fuel tank quantities.
# empty weight is 1/9 of full weight.
# content is 0.9 parts liquid fuel and 1.1 parts oxidizer.

FuelTank = namedtuple('FuelTank', ['name', 'size', 'cost', 'm_full'])

RocketFuelTanks = [
        FuelTank('Oscar-B', RadialSize.Tiny, 70, 225),               # 0
        FuelTank('FL-T100', RadialSize.Small, 150, 562.5),           # 1
        FuelTank('FL-T200', RadialSize.Small, 275, 1125),
        FuelTank('FL-T400', RadialSize.Small, 500, 2250),
        FuelTank('FL-T800', RadialSize.Small, 800, 4500),            # 4
        FuelTank('X200-8',  RadialSize.Large, 800, 4500),            # 5
        FuelTank('X200-16', RadialSize.Large, 1550, 9000),
        FuelTank('X200-32', RadialSize.Large, 3000, 18000),
        FuelTank('Jumbo-64',RadialSize.Large, 5750, 36000),          # 8
        FuelTank('S3-3600', RadialSize.ExtraLarge, 3250, 20250),     # 9
        FuelTank('S3-7200', RadialSize.ExtraLarge, 6500, 40500),
        FuelTank('S3-14400',RadialSize.ExtraLarge, 13000, 81000) ]   # 11

SmallestTank = { RadialSize.Tiny : 0, RadialSize.Small: 1, RadialSize.Large: 5, RadialSize.ExtraLarge: 9 }
BiggestTank =  { RadialSize.Tiny : 0, RadialSize.Small: 4, RadialSize.Large: 8, RadialSize.ExtraLarge: 11 }

TwinBoarPseudoTank = FuelTank('LFB Twin-Boar', RadialSize.Large, 5750, 36000)

class FuelTypes(Enum):
    LiquidFuel = ('Liquid fuel (+Oxidizer)', 5)
    AtomicFuel = ('Atomic fuel', 5)    # atomic fuel is liquid fuel w/out oxidizer
    Xenon = ('Xenon', 0.1)
    Monopropellant = ('Monopropellant', 4)
    def __init__(self, pname, unitmass):
        self.pname = pname
        self.unitmass = unitmass

SpecialFuelTank = namedtuple('SpecialFuelTank', ['name', 'size', 'cost', 'm_full', 'f_e', 'level'])

AtomicRocketMotor = Engine(RadialSize.Small, 'LV-N Nerv Atomic Rocket Motor', 10000, 3000,
        185, 800, 60000, 0, ResearchNode.NuclearPropulsion, 1, 3)
AtomicTankFactor = 23/45    # Mass of full atomic fuel tank / Mass of full liquid fuel tank
AtomicTank_f_e = 5/18

ElectricPropulsionSystem = Engine(RadialSize.Tiny, 'IX-6315 Dawn Electric Propulsion System',
        8000, 250, 100, 4200, 2000, 0, ResearchNode.IonPropulsion, 0, 0)
XenonTanks = [
    SpecialFuelTank('PB-X150', RadialSize.Tiny, 3600, 125, 11/14, ResearchNode.IonPropulsion),
    SpecialFuelTank('PB-X750', RadialSize.Small, 22500, 937.5, 11/14, ResearchNode.IonPropulsion),
    SpecialFuelTank('PB-X50R', RadialSize.RadiallyMounted, 2200, 71.4, 157/200, ResearchNode.IonPropulsion) ]

MonoPropellantEngine = \
        Engine(RadialSize.RadiallyMounted, 'O-10 Puff MonoPropellant Fuel Engine',
                      150, 90, 120, 250, 20000, 0, ResearchNode.PrecisionPropulsion, 0, 0)
MonoPropellantTanks = [
        SpecialFuelTank('FL-R10', RadialSize.Tiny,  200,  370, 5/32, ResearchNode.AdvancedFuelSystems),
        SpecialFuelTank('FL-R25', RadialSize.Small, 600,  1150, 3/20, ResearchNode.AdvancedFuelSystems),
        SpecialFuelTank('FL-R1',  RadialSize.Large, 1300, 3400, 2/15, ResearchNode.AdvancedFuelSystems),
        SpecialFuelTank('Stratus-V Roundified', RadialSize.RadiallyMounted, 200, 315, 5 / 16,
                        ResearchNode.AdvancedFlightControl),
        SpecialFuelTank('Stratus-V Cylindrified', RadialSize.RadiallyMounted, 450, 750, 1 / 4,
                        ResearchNode.SpecializedControl) ]

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
StackstageExtraTech = ResearchNode.Engineering101

# Extra for radial stage
# This is a very heavy but safe default setting, also having the effect of
# reducing the count of extra radial solid fuel boosters.
RadialstageExtraMass = 50 + 75 + 2*50
RadialstageExtraCost = 700 + 320 + 2*42
RadialstageExtraNote = "TT-70 Radial Decoupler, Advanced Nose Cone, 2 * EAS-4 Strut Connector"
RadialstageExtraTech = ResearchNode.Stability   # actually TT-70 is not there, but with TT-38K the
                                                # first radial decoupler.
