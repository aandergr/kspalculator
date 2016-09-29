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
        self.payload = payload
        self.mainengine = mainengine
        self.mainenginecount = mainenginecount
        self.eng_F_percentage = None
        self.size = size
        self.specialfueltype = None
        self.specialfuelunitmass = None
        self.fueltanks = [] # list of tuples (count,tank)
        self.notes = []
        self.sfb = None
        self.sfbcount = 0
        self.performance = None # returned by physics.*_performance()
        self.requiredscience = techtree.NodeSet()
        self.requiredscience.add(mainengine.level)
        self.features = set()
        self.is_best = False

    def get_cost(self):
        if self.sfb is None:
            sfbcost = 0
        else:
            sfbcost = self.sfbcount*self.sfb.cost + \
                      (parts.StackstageExtraCost if self.sfbcount == 1 else self.sfbcount*parts.RadialstageExtraCost)
        fuelcost = sum([tp[0]*tp[1].cost for tp in self.fueltanks])
        if self.specialfueltype == "Atomic fuel":
            fuelcost -= self.get_fueltankmass()/(1+self.mainengine.f_e)*1.1/0.9*0.04
        return self.mainenginecount*self.mainengine.cost + sfbcost + fuelcost

    def get_fueltankmass(self):
        fuelmass = sum([tp[0]*tp[1].m_full for tp in self.fueltanks])
        if self.specialfueltype == "Atomic fuel":
            fuelmass *= parts.AtomicTankFactor
        return fuelmass

    def get_sfbmountmass(self):
        return parts.StackstageExtraMass if self.sfbcount == 1 else self.sfbcount*parts.RadialstageExtraMass

    def get_mass(self):
        if self.sfb is None:
            sfbmass = 0
        else:
            sfbmass = self.sfbcount*self.sfb.m_full + self.get_sfbmountmass()
        return self.payload + self.mainenginecount*self.mainengine.m + sfbmass + self.get_fueltankmass()

    def add_sfb(self, sfb, sfbcount):
        self.sfb = sfb
        self.requiredscience.add(sfb.level)
        self.sfbcount = sfbcount
        if sfbcount == 1:
            self.requiredscience.add(parts.StackstageExtraTech)
            self.notes.append("Vertically stacked %s SFB" % sfb.name)
            self.notes.append("SFB mounted on %s" % parts.StackstageExtraNote)
        else:
            self.requiredscience.add(parts.RadialstageExtraTech)
            self.notes.append("Radially attached %i * %s SFB" % (sfbcount, sfb.name))
            self.notes.append("SFBs mounted on %s each" % parts.RadialstageExtraNote)
    def add_liquidfuel_tanks(self, lf):
        # lf is full tank mass
        if self.mainengine.name == "LFB Twin-Boar":
            lf = max(lf, 36000)
            self.notes.append("6400 units of liquid fuel are already included in the engine")
        smalltankcount = ceil(lf / parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full)
        # Fuel tank calculation:
        # We use that
        # - Tank size is 2^n times the size of smallest tank with that radius
        # - It is cheapest to use the biggest tank possible
        for i in range(parts.SmallestTank[self.size], parts.BiggestTank[self.size]+1):
            if i != parts.BiggestTank[self.size]:
                if smalltankcount % 2 != 0:
                    self.fueltanks.append((1, parts.RocketFuelTanks[i]))
                smalltankcount = smalltankcount // 2
            else:
                if self.mainengine.name == "LFB Twin-Boar":
                    smalltankcount -= 1
                    if smalltankcount > 0:
                        self.fueltanks.append((smalltankcount, parts.RocketFuelTanks[i]))
                    self.fueltanks.append((1, parts.TwinBoarPseudoTank))
                else:
                    self.fueltanks.append((smalltankcount, parts.RocketFuelTanks[i]))
    def add_atomic_tanks(self, af):
        # af is full tank mass
        # Adomic Fuel is liquid fuel without oxidizer.
        f_f = parts.AtomicTankFactor
        smalltankcount = ceil(af / (parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full*f_f))
        self.specialfueltype = "Atomic fuel"
        self.specialfuelunitmass = 5
        self.notes.append("Atomic fuel is regular liquid fuel w/out oxidizer (remove oxidizer in VAB!)")
        # Fuel tank calculation:
        # We use that
        # - Tank size is 2^n times the size of smallest tank with that radius
        # - It is cheapest to use the biggest tank possible
        for i in range(parts.SmallestTank[self.size], parts.BiggestTank[self.size]+1):
            if i != parts.BiggestTank[self.size]:
                if smalltankcount % 2 != 0:
                    self.fueltanks.append((1, parts.RocketFuelTanks[i]))
                smalltankcount = smalltankcount // 2
            else:
                self.fueltanks.append((smalltankcount, parts.RocketFuelTanks[i]))
    def add_xenon_tanks(self, xf):
        # xf is full tank mass
        tankcount = ceil(xf / parts.XenonTank.m_full)
        self.specialfueltype = "Xenon"
        self.specialfuelunitmass = parts.XenonUnitMass
        self.fueltanks.append((tankcount, parts.XenonTank))
    def add_monopropellant_tanks(self, mp, tank):
        # mp is full tank mass
        tankcount = ceil(mp / tank.m_full)
        self.specialfueltype = "MonoPropellant"
        self.specialfuelunitmass = parts.MonoPropellantUnitMass
        self.requiredscience.add(parts.MonoPropellantTankTech)
        self.fueltanks.append((tankcount, tank))

    def calculate_performance(self, dv, pressure):
        fueltankmass = self.get_fueltankmass()
        sfbmountmass = self.get_sfbmountmass()
        if self.sfb is None and self.specialfueltype is None:
            # liquid fuel only
            self.performance = physics.lf_performance(dv,
                    physics.engine_isp(self.mainengine, pressure),
                    physics.engine_force(self.mainenginecount, self.mainengine, pressure),
                    pressure, self.get_mass() - fueltankmass, fueltankmass*8/9, 1/8)
        elif self.sfb is None and self.specialfueltype is not None:
            # atomic fuel, monopropellant or xenon
            f_e = self.mainengine.f_e
            self.performance = physics.lf_performance(dv,
                    physics.engine_isp(self.mainengine, pressure),
                    physics.engine_force(self.mainenginecount, self.mainengine, pressure),
                    pressure, self.get_mass() - fueltankmass, fueltankmass/(1+f_e), f_e)
        else:
            # liquid fuel + solid fuel
            self.performance = physics.sflf_concurrent_performance(dv,
                    physics.engine_isp(self.mainengine, pressure),
                    physics.engine_isp(self.sfb, pressure),
                    physics.engine_force(self.mainenginecount, self.mainengine, pressure),
                    physics.engine_force(self.sfbcount, self.sfb, pressure),
                    pressure,
                    self.get_mass() - fueltankmass - sfbmountmass - self.sfbcount*self.sfb.m_full,
                    fueltankmass*8/9,
                    sfbmountmass,
                    self.sfbcount*self.sfb.m_full,
                    self.sfbcount*self.sfb.m_empty,
                    self.eng_F_percentage)

    def has_enough_acceleration(self, min_acceleration):
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
                 (f_yes if Features.mass in self.features else f_no, self.get_mass()))
        rstr += ("%sCost: %.0f\n" %
                 (f_yes if Features.cost in self.features else f_no, self.get_cost()))
        fueltankmass = self.get_fueltankmass()
        if self.specialfueltype is None:
            rstr += ("\tLiquid fuel: %.0f units (%.0f kg full tank mass)\n" %
                     (fueltankmass * 8 / 9 * 0.2, fueltankmass))
        else:
            rstr += ("%s%s: %.0f units (%.0f kg full tank mass)\n" %
                     (f_yes if Features.monopropellant in self.features else f_no,
                      self.specialfueltype,
                      fueltankmass / (self.mainengine.f_e + 1) / self.specialfuelunitmass,
                      fueltankmass))
        rstr += "\tFuel tanks: %s\n" % ", ".join(("%i * %s" % (t[0], t[1].name) for t in self.fueltanks))
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

    def is_better_than(self, a, preferredsize, bestgimbal, prefergenerators, prefershortengines, prefermonopropellant):
        """
        Returns True if self is better than a by any parameter, i.e. there might
        be a reason to use self instead of a.
        """
        # obvious and easy to check criteria
        if (self.get_mass() < a.get_mass()) or (self.get_cost() < a.get_cost()):
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
            if not e.is_best:
                continue
            if lowest_mass and e.get_mass() < self.get_mass():
                lowest_mass = False
            if lowest_cost and e.get_cost() < self.get_cost():
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
                techtree.Node.HypersonicFlight not in self.requiredscience.nodes and
                techtree.Node.IonPropulsion not in self.requiredscience.nodes):
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


def create_single_lfe_design(payload, pressure, dv, acc, eng):
    design = Design(payload, eng, 1, eng.size)
    lf = physics.lf_needed_fuel(dv, physics.engine_isp(eng, pressure), design.get_mass(), 1/8)
    if lf is None:
        return None
    design.add_liquidfuel_tanks(9 / 8 * lf)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    return design

def create_atomic_design(payload, pressure, dv, acc):
    design = Design(payload, parts.AtomicRocketMotor, 1, parts.RadialSize.Small)
    f_e = parts.AtomicRocketMotor.f_e
    af = physics.lf_needed_fuel(dv, physics.engine_isp(parts.AtomicRocketMotor, pressure),
            design.get_mass(), f_e)
    if af is None:
        return None
    design.add_atomic_tanks((1 + f_e) * af)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    return design

def create_xenon_design(payload, pressure, dv, acc):
    design = Design(payload, parts.ElectricPropulsionSystem, 1, parts.RadialSize.Tiny)
    f_e = parts.ElectricPropulsionSystem.f_e
    xf = physics.lf_needed_fuel(dv, physics.engine_isp(parts.ElectricPropulsionSystem, pressure),
            design.get_mass(), f_e)
    if xf is None:
        return None
    design.add_xenon_tanks((1 + f_e) * xf)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    return design

def create_monopropellant_design(payload, pressure, dv, acc, engine, tank, count):
    design = Design(payload, engine, count, tank.size)
    f_e = engine.f_e
    mp = physics.lf_needed_fuel(dv, physics.engine_isp(engine, pressure),
            design.get_mass(), f_e)
    if mp is None:
        return None
    design.add_monopropellant_tanks((1 + f_e) * mp, tank)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    return design

def create_single_lfe_sfb_design(payload, pressure, dv, acc, eng, eng_F_percentage, sfb, sfbcount):
    design = Design(payload, eng, 1, eng.size)
    design.add_sfb(sfb, sfbcount)
    # lpsr = Fl * I_sps / Fs / I_spl
    lpsr = eng.F_vac * sfb.isp_vac / sfbcount / sfb.F_vac / eng.isp_vac
    design.eng_F_percentage = eng_F_percentage
    lf = physics.sflf_concurrent_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.get_mass() - design.get_sfbmountmass() - sfbcount*sfb.m_full,
            design.get_sfbmountmass(), sfbcount*sfb.m_full, sfbcount*sfb.m_empty, lpsr*eng_F_percentage)
    if lf is None:
        return None
    design.add_liquidfuel_tanks(9 / 8 * lf)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    if sfbcount != 1:
        design.notes.append("Set liquid fuel engine thrust to {:.0%} while SFB are burning".format(eng_F_percentage))
    return design

def create_radial_lfe_design(payload, pressure, dv, acc, eng, size, count):
    design = Design(payload, eng, count, size)
    lf = physics.lf_needed_fuel(dv, physics.engine_isp(eng, pressure), design.get_mass(), 1/8)
    if lf is None:
        return None
    design.add_liquidfuel_tanks(9 / 8 * lf)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    return design

def create_radial_lfe_sfb_design(payload, pressure, dv, acc, eng, eng_F_percentage, size, count, sfb, sfbcount):
    design = Design(payload, eng, count, size)
    design.add_sfb(sfb, sfbcount)
    # lpsr = Fl * I_sps / Fs / I_spl
    lpsr = count * eng.F_vac * sfb.isp_vac / sfbcount / sfb.F_vac / eng.isp_vac
    design.eng_F_percentage = eng_F_percentage
    lf = physics.sflf_concurrent_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.get_mass() - design.get_sfbmountmass() - sfbcount*sfb.m_full,
            design.get_sfbmountmass(), sfbcount*sfb.m_full, sfbcount*sfb.m_empty, lpsr*eng_F_percentage)
    if lf is None:
        return None
    design.add_liquidfuel_tanks(9 / 8 * lf)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    if sfbcount != 1:
        design.notes.append("Set liquid fuel engine thrust to {:.0%} while SFB are burning".format(eng_F_percentage))
    return design

def find_designs(payload, pressure, dv, min_acceleration,
                 preferredsize = None, bestgimbal = 0, sfballowed = False, prefergenerators = False,
                 prefershortengines = False, prefermonopropellant = True):
    # pressure: 0 = vacuum, 1 = kerbin
    designs = []
    d = create_atomic_design(payload, pressure, dv, min_acceleration)
    if d is not None:
        designs.append(d)
    d = create_xenon_design(payload, pressure, dv, min_acceleration)
    if d is not None:
        designs.append(d)
    for i in range(len(parts.MonoPropellantTanks)):
        for count in [2, 3, 4, 6, 8]:
            d = create_monopropellant_design(payload, pressure, dv, min_acceleration,
                                             parts.MonoPropellantEngines[i], parts.MonoPropellantTanks[i], count)
            if d is not None:
                designs.append(d)
                break  # do not try more engines as it wouldn't have any advantage
    for eng in parts.LiquidFuelEngines:
        if eng.size is parts.RadialSize.RdMntd:
            for size in [parts.RadialSize.Tiny, parts.RadialSize.Small,
                    parts.RadialSize.Large, parts.RadialSize.ExtraLarge]:
                for count in [2, 3, 4, 6, 8]:
                    d = create_radial_lfe_design(payload, pressure, dv, min_acceleration,
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
                                    d = create_radial_lfe_sfb_design(payload, pressure, dv, min_acceleration,
                                                                     eng, limit, size, count, sfb, sfbcount)
                                    if d is not None:
                                        designs.append(d)
                                    if sfbcount == 1:
                                        break
        else:
            d = create_single_lfe_design(payload, pressure, dv, min_acceleration, eng)
            if d is not None:
                designs.append(d)
            if sfballowed and eng.size is not parts.RadialSize.Tiny:
                for sfbcount in [1, 2, 3, 4, 6, 8]:
                    if sfbcount == 1 and eng.size is not parts.RadialSize.Small:
                        # would look bad
                        continue
                    for sfb in parts.SolidFuelBoosters:
                        for limit in [0, 1/3, 1/2, 2/3, 1]:
                            d = create_single_lfe_sfb_design(payload, pressure, dv, min_acceleration,
                                                             eng, limit, sfb, sfbcount)
                            if d is not None:
                                designs.append(d)
                            if sfbcount == 1:
                                break
    for d in designs:
        d.is_best = True
        for e in designs:
            if (d is not e) and (not d.is_better_than(e, preferredsize, bestgimbal, prefergenerators,
                                                      prefershortengines, prefermonopropellant)):
                d.is_best = False
                break

    # determine which are the features of d, i.e. why it is the best
    for d in designs:
        if not d.is_best:
            continue
        d.determine_features(designs, preferredsize, bestgimbal, prefergenerators,
                             prefershortengines, prefermonopropellant)

    return designs
