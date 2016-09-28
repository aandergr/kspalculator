# -*- coding: utf-8 -*-
# Python 2.7 support.
from __future__ import division

import enum
from math import ceil

from . import parts
from . import physics
from . import techtree

@enum.unique
class Features(enum.Enum):
    """List of criteria by which one Design can be the best."""
    mass = 1
    cost = 2
    low_requirements = 3
    gimbal = 4
    short_engine = 5
    monopropellant = 6
    generator = 7
    radial_size = 8


class Design:
    def __init__(self, payload, mainengine, mainenginecount, size):
        self.mass = payload + mainenginecount*mainengine.m
        self.cost = mainenginecount * mainengine.cost
        self.mainengine = mainengine
        self.mainenginecount = mainenginecount
        self.lpsr = None
        self.size = size
        self.liquidfuel = None
        self.specialfuel = None
        self.specialfueltype = None
        self.specialfuelunitmass = None
        self.notes = []
        self.sfb = None
        self.sfbcount = 0
        self.sfbmountmass = 0
        self.performance = None # returned by physics.*_performance()
        self.requiredscience = techtree.NodeSet()
        self.requiredscience.add(mainengine.level)
        self.features = set()
        self.IsBest = False
    def AddSFB(self, sfb, sfbcount):
        self.sfb = sfb
        self.requiredscience.add(sfb.level)
        self.sfbcount = sfbcount
        if sfbcount == 1:
            self.sfbmountmass = parts.StackstageExtraMass
            self.cost = self.cost + parts.StackstageExtraCost
            self.requiredscience.add(parts.StackstageExtraTech)
            self.notes.append("Vertically stacked %s SFB" % sfb.name)
            self.notes.append("SFB mounted on %s" % parts.StackstageExtraNote)
        else:
            self.sfbmountmass = sfbcount*parts.RadialstageExtraMass
            self.cost = self.cost + sfbcount*parts.RadialstageExtraCost
            self.requiredscience.add(parts.RadialstageExtraTech)
            self.notes.append("Radially attached %i * %s SFB" % (sfbcount, sfb.name))
            self.notes.append("SFBs mounted on %s each" % parts.RadialstageExtraNote)
        self.mass = self.mass + self.sfbmountmass + sfbcount*sfb.m_full
        self.cost = self.cost + sfbcount*sfb.cost
    def AddLiquidFuelTanks(self, lf):
        # lf is full tank mass
        if self.mainengine.name == "LFB Twin-Boar":
            lf = max(lf, 36000)
            self.notes.append("6400 units of liquid fuel are already included in the engine")
        smalltankcount = ceil(lf / parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full)
        self.liquidfuel = smalltankcount * parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full
        self.mass = self.mass + self.liquidfuel
        # Fuel tank calculation:
        # We use that
        # - Tank size is 2^n times the size of smallest tank with that radius
        # - It is cheapest to use the biggest tank possible
        for i in range(parts.SmallestTank[self.size], parts.BiggestTank[self.size]+1):
            if i != parts.BiggestTank[self.size]:
                if smalltankcount % 2 != 0:
                    self.cost = self.cost + parts.RocketFuelTanks[i].cost
                smalltankcount = smalltankcount // 2
            else:
                self.cost = self.cost + smalltankcount * parts.RocketFuelTanks[i].cost
    def AddAtomicFuelTanks(self, af):
        # af is full tank mass
        # Adomic Fuel is liquid fuel without oxidizer.
        f_f = parts.AtomicTankFactor
        f_e = self.mainengine.f_e
        smalltankcount = ceil(af / (parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full*f_f))
        self.specialfuel = smalltankcount * parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full*f_f
        self.specialfueltype = "Atomic fuel"
        self.specialfuelunitmass = 5
        self.notes.append("Atomic fuel is regular liquid fuel w/out oxidizer (remove oxidizer in VAB!)")
        self.mass = self.mass + self.specialfuel
        # Fuel tank calculation:
        # We use that
        # - Tank size is 2^n times the size of smallest tank with that radius
        # - It is cheapest to use the biggest tank possible
        for i in range(parts.SmallestTank[self.size], parts.BiggestTank[self.size]+1):
            if i != parts.BiggestTank[self.size]:
                if smalltankcount % 2 != 0:
                    self.cost = self.cost + parts.RocketFuelTanks[i].cost
                smalltankcount = smalltankcount // 2
            else:
                self.cost = self.cost + smalltankcount * parts.RocketFuelTanks[i].cost
        # black magic to quit cost of saved oxidizer
        self.cost = self.cost - self.specialfuel/(1+f_e)*1.1/0.9*0.04
    def AddXenonTanks(self, xf):
        # xf is full tank mass
        tankcount = ceil(xf / parts.XenonTank.m_full)
        self.specialfuel = tankcount * parts.XenonTank.m_full
        self.specialfueltype = "Xenon"
        self.specialfuelunitmass = parts.XenonUnitMass
        self.mass = self.mass + self.specialfuel
        self.cost = self.cost + tankcount*parts.XenonTank.cost
    def AddMonoPropellantTanks(self, mp, tank):
        # mp is full tank mass
        tankcount = ceil(mp / tank.m_full)
        self.specialfuel = tankcount * tank.m_full
        self.specialfueltype = "MonoPropellant"
        self.specialfuelunitmass = parts.MonoPropellantUnitMass
        self.mass = self.mass + self.specialfuel
        self.cost = self.cost + tankcount*tank.cost
        self.requiredscience.add(parts.MonoPropellantTankTech)
    def CalculatePerformance(self, dv, pressure):
        if self.sfb is None and self.liquidfuel is not None:
            # liquid fuel only
            self.performance = physics.lf_performance(dv,
                    physics.engine_isp(self.mainengine, pressure),
                    physics.engine_force(self.mainenginecount, self.mainengine, pressure),
                    pressure, self.mass - self.liquidfuel, self.liquidfuel*8/9, 1/8)
        elif self.sfb is None and self.liquidfuel is None:
            # atomic fuel, monopropellant or xenon
            f_e = self.mainengine.f_e
            self.performance = physics.lf_performance(dv,
                    physics.engine_isp(self.mainengine, pressure),
                    physics.engine_force(self.mainenginecount, self.mainengine, pressure),
                    pressure, self.mass - self.specialfuel, self.specialfuel/(1+f_e), f_e)
        else:
            # liquid fuel + solid fuel
            self.performance = physics.sflf_concurrent_performance(dv,
                    physics.engine_isp(self.mainengine, pressure),
                    physics.engine_isp(self.sfb, pressure),
                    physics.engine_force(self.mainenginecount, self.mainengine, pressure),
                    physics.engine_force(self.sfbcount, self.sfb, pressure),
                    pressure,
                    self.mass - self.liquidfuel - self.sfbmountmass - self.sfbcount*self.sfb.m_full,
                    self.liquidfuel*8/9,
                    self.sfbmountmass,
                    self.sfbcount*self.sfb.m_full,
                    self.sfbcount*self.sfb.m_empty,
                    self.lpsr)
    def EnoughAcceleration(self, min_acceleration):
        if self.performance is None:
            return False
        # pylint: disable=unused-variable
        dv, p, a_s, a_t, m_s, m_t, solid, op = self.performance
        for i in range(len(a_s)):
            if a_s[i] < min_acceleration[op[i]]:
                return False
        return True

    def __str__(self):
        rstr = ''
        f_yes = '      ✔ '
        f_no = '\t'
        if self.mainenginecount == 1:
            rstr += "%s\n" % self.mainengine.name
        else:
            rstr += "%i * %s, radially mounted\n" % (self.mainenginecount, self.mainengine.name)
        rstr += ("%sTotal Mass: %.0f kg (including payload and full tanks)\n" %
                 (f_yes if Features.mass in self.features else f_no, self.mass))
        rstr += ("%sCost: %.0f\n" %
                 (f_yes if Features.cost in self.features else f_no, self.cost))
        if self.liquidfuel is not None:
            rstr += ("\tLiquid fuel: %.0f units (%.0f kg full tank mass)\n" %
                     (self.liquidfuel * 8 / 9 * 0.2, self.liquidfuel))
        if self.specialfuel is not None:
            rstr += ("%s%s: %.0f units (%.0f kg full tank mass)\n" %
                     (f_yes if Features.monopropellant in self.features else f_no,
                      self.specialfueltype,
                      self.specialfuel / (self.mainengine.f_e + 1) / self.specialfuelunitmass,
                      self.specialfuel))
        rstr += ("%sRequires: %s\n" %
                 (f_yes if Features.low_requirements in self.features else f_no,
                  ", ".join([n.name for n in self.requiredscience.nodes])))
        rstr += ("%sRadial size: %s\n" %
                 (f_yes if Features.radial_size in self.features else f_no, self.size.name))
        if self.mainengine.tvc != 0.0:
            rstr += ("%sGimbal: %.1f °\n" %
                     (f_yes if Features.gimbal in self.features else f_no, self.mainengine.tvc))
        if self.mainengine.electricity == 1:
            rstr += ("%sEngine generates electricity\n" %
                     (f_yes if Features.generator in self.features else f_no))
        length = None
        if self.mainengine.length == 0:
            length = "LT-05 Micro Landing Struts"
        elif self.mainengine.length == 1:
            length = "LT-1 Landing Struts"
        elif self.mainengine.length == 2:
            length = "LT-2 Landing Struts"
        if self.mainengine.length <= 2:
            rstr += ("%sEngine is short enough to be used with %s\n" %
                     (f_yes if Features.short_engine in self.features else f_no, length))
        for n in self.notes:
            rstr += "\t%s\n" % n
        rstr += "\tPerformance:\n"
        dv, p, a_s, a_t, m_s, m_t, solid, dummy = self.performance
        for i in range(len(dv)):
            p_str = ("%.2f atm" % p[i]) if p[i] > 0 else "vacuum  "
            solid_str = "*" if solid[i] else " "
            rstr += ("\t %s%i:  %4.0f m/s @ %s  %5.2f m/s² - %5.2f m/s²  %5.1f t - %5.1f t\n" %
                     (solid_str, i + 1, dv[i], p_str, a_s[i], a_t[i],
                      m_s[i] / 1000.0, m_t[i] / 1000.0))
        return rstr

    def IsBetterThan(self, a, preferredsize, bestgimbal, prefergenerators, prefershortengines, prefermonopropellant):
        """
        Returns True if self is better than a by any parameter, i.e. there might
        be a reason to use self instead of a.
        """
        # obvious and easy to check criteria
        if (self.mass < a.mass) or (self.cost < a.cost):
            return True
        # if user requires, check if we have better gimbal
        if bestgimbal == 1:
            if self.mainengine.tvc > 0.0 and a.mainengine.tvc == 0.0:
                return True
        elif bestgimbal >= 2:
            if self.mainengine.tvc > a.mainengine.tvc:
                return True
        # using monopropellant engine might be an advantage
        if prefermonopropellant and \
                (self.specialfueltype is not None and self.specialfueltype == "MonoPropellant") and \
                (a.specialfueltype is None or a.specialfueltype != "MonoPropellant"):
            return True
        # if user cares about whether engine generates electricity
        if prefergenerators and self.mainengine.electricity == 1 and a.mainengine.electricity == 0:
            return True
        # engine length
        if prefershortengines and self.mainengine.length < a.mainengine.length:
            return True
        # this is where user's size preferrence comes in
        if preferredsize is not None:
            if self.size is preferredsize and a.size is not preferredsize:
                return True
        # to be earlier available in the game is an advantage
        if self.requiredscience.is_easier_than(a.requiredscience):
            return True
        return False

    def determine_features(self, designs, preferredsize, bestgimbal, prefergenerators,
                           prefershortengines, prefermonopropellant):
        """Sets self.features according to properties of design.Features enum."""
        lowest_mass = True
        lowest_cost = True
        lowest_requirements = True
        best_gimbal_range = True
        shortest_engine = True
        for e in designs:
            if not e.IsBest:
                continue
            if lowest_mass and e.mass < self.mass:
                lowest_mass = False
            if lowest_cost and e.cost < self.cost:
                lowest_cost = False
            if lowest_requirements and e.requiredscience.is_easier_than(self.requiredscience):
                lowest_requirements = False
            if best_gimbal_range and e.mainengine.tvc > self.mainengine.tvc:
                best_gimbal_range = False
            if shortest_engine and e.mainengine.length < self.mainengine.length:
                shortest_engine = False
        if lowest_mass:
            self.features.add(Features.mass)
        if lowest_cost:
            self.features.add(Features.cost)
        if lowest_requirements:
            # this extra condition is false, but it looks strange if requiring 'only'
            # VeryHeavRocketry is presented as something good
            if (techtree.Node.VeryHeavyRocketry not in self.requiredscience.nodes and
                techtree.Node.HypersonicFlight not in self.requiredscience.nodes):
                self.features.add(Features.low_requirements)
        if prefershortengines and shortest_engine:
            self.features.add(Features.short_engine)
        if ((bestgimbal == 1 and self.mainengine.tvc > 0.0) or
            (bestgimbal == 2 and best_gimbal_range)):
            self.features.add(Features.gimbal)
        if (prefermonopropellant and self.specialfueltype is not None and
            self.specialfueltype == "MonoPropellant"):
            self.features.add(Features.monopropellant)
        if prefergenerators and self.mainengine.electricity:
            self.features.add(Features.generator)
        if preferredsize is not None and self.size is preferredsize:
            self.features.add(Features.radial_size)


def CreateSingleLFEngineDesign(payload, pressure, dv, acc, eng):
    design = Design(payload, eng, 1, eng.size)
    lf = physics.lf_needed_fuel(dv, physics.engine_isp(eng, pressure), design.mass, 1/8)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    return design

def CreateAtomicRocketMotorDesign(payload, pressure, dv, acc):
    design = Design(payload, parts.AtomicRocketMotor, 1, parts.RadialSize.Small)
    f_e = parts.AtomicRocketMotor.f_e
    af = physics.lf_needed_fuel(dv, physics.engine_isp(parts.AtomicRocketMotor, pressure),
            design.mass, f_e)
    if af is None:
        return None
    design.AddAtomicFuelTanks((1+f_e) * af)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    return design

def CreateElectricPropulsionSystemDesign(payload, pressure, dv, acc):
    design = Design(payload, parts.ElectricPropulsionSystem, 1, parts.RadialSize.Tiny)
    f_e = parts.ElectricPropulsionSystem.f_e
    xf = physics.lf_needed_fuel(dv, physics.engine_isp(parts.ElectricPropulsionSystem, pressure),
            design.mass, f_e)
    if xf is None:
        return None
    design.AddXenonTanks((1+f_e) * xf)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    return design

def CreateMonoPropellantEngineDesign(payload, pressure, dv, acc, engine, tank, count):
    design = Design(payload, engine, count, tank.size)
    f_e = engine.f_e
    mp = physics.lf_needed_fuel(dv, physics.engine_isp(engine, pressure),
            design.mass, f_e)
    if mp is None:
        return None
    design.AddMonoPropellantTanks((1+f_e) * mp, tank)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    return design

def CreateSingleLFESFBDesign(payload, pressure, dv, acc, eng, eng_F_percentage, sfb, sfbcount):
    design = Design(payload, eng, 1, eng.size)
    design.AddSFB(sfb, sfbcount)
    # lpsr = Fl * I_sps / Fs / I_spl
    design.lpsr = eng_F_percentage * eng.F_vac * sfb.isp_vac / sfb.F_vac / eng.isp_vac
    lf = physics.sflf_concurrent_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.mass - design.sfbmountmass - sfbcount*sfb.m_full,
            design.sfbmountmass, sfbcount*sfb.m_full, sfbcount*sfb.m_empty, design.lpsr)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    if sfbcount != 1:
        design.notes.append("Set liquid fuel engine thrust to {:.0%} while SFB are burning".format(eng_F_percentage))
    return design

def CreateRadialLFEnginesDesign(payload, pressure, dv, acc, eng, size, count):
    design = Design(payload, eng, count, size)
    lf = physics.lf_needed_fuel(dv, physics.engine_isp(eng, pressure), design.mass, 1/8)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    return design

def CreateRadialLFESFBDesign(payload, pressure, dv, acc, eng, eng_F_percentage, size, count, sfb, sfbcount):
    design = Design(payload, eng, count, size)
    design.AddSFB(sfb, sfbcount)
    # lpsr = Fl * I_sps / Fs / I_spl
    design.lpsr = eng_F_percentage * eng.F_vac * sfb.isp_vac / sfb.F_vac / eng.isp_vac
    lf = physics.sflf_concurrent_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.mass - design.sfbmountmass - sfbcount*sfb.m_full,
            design.sfbmountmass, sfbcount*sfb.m_full, sfbcount*sfb.m_empty, design.lpsr)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    if sfbcount != 1:
        design.notes.append("Set liquid fuel engine thrust to {:.0%} while SFB are burning".format(eng_F_percentage))
    return design

def FindDesigns(payload, pressure, dv, min_acceleration,
        preferredsize = None, bestgimbal = 0, sfballowed = False, prefergenerators = False,
        prefershortengines = False, prefermonopropellant = True):
    # pressure: 0 = vacuum, 1 = kerbin
    designs = []
    d = CreateAtomicRocketMotorDesign(payload, pressure, dv, min_acceleration)
    if d is not None:
        designs.append(d)
    d = CreateElectricPropulsionSystemDesign(payload, pressure, dv, min_acceleration)
    if d is not None:
        designs.append(d)
    for i in range(len(parts.MonoPropellantTanks)):
        for count in [2, 3, 4, 6, 8]:
            d = CreateMonoPropellantEngineDesign(payload, pressure, dv, min_acceleration,
                    parts.MonoPropellantEngines[i], parts.MonoPropellantTanks[i], count)
            if d is not None:
                designs.append(d)
                break  # do not try more engines as it wouldn't have any advantage
    for eng in parts.LiquidFuelEngines:
        if eng.size is parts.RadialSize.RdMntd:
            for size in [parts.RadialSize.Tiny, parts.RadialSize.Small,
                    parts.RadialSize.Large, parts.RadialSize.ExtraLarge]:
                for count in [2, 3, 4, 6, 8]:
                    d = CreateRadialLFEnginesDesign(payload, pressure, dv, min_acceleration,
                            eng, size, count)
                    if d is not None:
                        designs.append(d)
                        break   # do not try more engines
                if sfballowed and size is not parts.RadialSize.Tiny:
                    for count in [2, 3, 4, 6, 8]:
                        for sfbcount in [1, 2, 3, 4, 6, 8]:
                            if sfbcount == 1 and size is not parts.RadialSize.Small:
                                # would look bad
                                continue
                            for sfb in parts.SolidFuelBoosters:
                                for limit in [0, 1/3, 1/2, 2/3, 1]:
                                    d = CreateRadialLFESFBDesign(payload, pressure, dv, min_acceleration,
                                            eng, limit, size, count, sfb, sfbcount)
                                    if d is not None:
                                        designs.append(d)
                                    if sfbcount == 1:
                                        break
        else:
            d = CreateSingleLFEngineDesign(payload, pressure, dv, min_acceleration, eng)
            if d is not None:
                designs.append(d)
            if sfballowed and eng.size is not parts.RadialSize.Tiny:
                for sfbcount in [1, 2, 3, 4, 6, 8]:
                    if sfbcount == 1 and eng.size is not parts.RadialSize.Small:
                        # would look bad
                        continue
                    for sfb in parts.SolidFuelBoosters:
                        for limit in [0, 1/3, 1/2, 2/3, 1]:
                            d = CreateSingleLFESFBDesign(payload, pressure, dv, min_acceleration,
                                    eng, limit, sfb, sfbcount)
                            if d is not None:
                                designs.append(d)
                            if sfbcount == 1:
                                break
    for d in designs:
        d.IsBest = True
        for e in designs:
            if (d is not e) and (not d.IsBetterThan(e, preferredsize, bestgimbal, prefergenerators,
                                                    prefershortengines, prefermonopropellant)):
                d.IsBest = False
                break

    # determine which are the features of d, i.e. why it is the best
    for d in designs:
        if not d.IsBest:
            continue
        d.determine_features(designs, preferredsize, bestgimbal, prefergenerators,
                             prefershortengines, prefermonopropellant)

    return designs
