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
    def __init__(self, payload, mainengine, mainenginecount, size, fueltype):
        self.payload = payload
        self.mainengine = mainengine
        self.mainenginecount = mainenginecount
        self.eng_F_percentage = None
        self.size = size
        self.fueltype = fueltype
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
        if self.fueltype is parts.FuelTypes.AtomicFuel:
            fuelcost -= self.get_fueltankmass()/(1+parts.AtomicTank_f_e)*1.1/0.9*0.04
        return self.mainenginecount*self.mainengine.cost + sfbcost + fuelcost

    def get_fueltankmass(self):
        fuelmass = sum([tp[0]*tp[1].m_full for tp in self.fueltanks])
        if self.fueltype is parts.FuelTypes.AtomicFuel:
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

    def add_conventional_tanks(self, lf):
        """Adds liquid fuel or atomic fuel tanks to design

        :param lf: full tank mass
        """
        if self.mainengine.name == "LFB Twin-Boar":
            lf = max(lf, 36000)
            self.notes.append("6400 units of liquid fuel are already included in the engine")
        if self.fueltype is parts.FuelTypes.LiquidFuel:
            smalltankcount = ceil(lf / parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full)
        else:
            # atomic fuel
            # Adomic Fuel is liquid fuel without oxidizer.
            smalltankcount = ceil(lf / (parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full *
                                        parts.AtomicTankFactor))
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
                if self.mainengine.name == "LFB Twin-Boar":
                    smalltankcount -= 1
                    if smalltankcount > 0:
                        self.fueltanks.append((smalltankcount, parts.RocketFuelTanks[i]))
                    self.fueltanks.append((1, parts.TwinBoarPseudoTank))
                else:
                    if smalltankcount > 0:
                        self.fueltanks.append((smalltankcount, parts.RocketFuelTanks[i]))

    def add_special_tanks(self, xf, tank):
        """Add Monopropellant or Xenon tanks to design

        :param xf: full tank mass
        :param tank: Tank model to add
        :type tank: parts.SpecialFuelTank
        """
        tankcount = ceil(xf / tank.m_full)
        if tank.size == parts.RadialSize.RadiallyMounted:
            tankcount = max(tankcount, 2)
        self.requiredscience.add(tank.level)
        self.fueltanks.append((tankcount, tank))

    def get_f_e(self):
        if self.fueltype is parts.FuelTypes.LiquidFuel:
            return 1 / 8
        elif self.fueltype is parts.FuelTypes.AtomicFuel:
            return parts.AtomicTank_f_e
        else:
            return self.fueltanks[0][1].f_e

    def calculate_performance(self, dv, pressure):
        fueltankmass = self.get_fueltankmass()
        if self.sfb is None:
            # liquid fuel only or
            # atomic fuel, monopropellant or xenon
            f_e = self.get_f_e()
            self.performance = \
                physics.lf_performance(dv,
                                       physics.engine_isp(self.mainengine, pressure),
                                       physics.engine_force(self.mainenginecount, self.mainengine,
                                                            pressure),
                                       pressure,
                                       self.payload + self.mainenginecount * self.mainengine.m,
                                       fueltankmass / (1 + f_e), f_e)
        else:
            # liquid fuel + solid fuel
            sfbmountmass = self.get_sfbmountmass()
            self.performance = \
                physics.sflf_concurrent_performance(dv,
                                                    physics.engine_isp(self.mainengine, pressure),
                                                    physics.engine_isp(self.sfb, pressure),
                                                    physics.engine_force(self.mainenginecount,
                                                                         self.mainengine, pressure),
                                                    physics.engine_force(self.sfbcount, self.sfb,
                                                                         pressure),
                                                    pressure,
                                                    self.payload + self.mainenginecount * self.mainengine.m,
                                                    fueltankmass * 8 / 9,
                                                    sfbmountmass,
                                                    self.sfbcount * self.sfb.m_full,
                                                    self.sfbcount * self.sfb.m_empty,
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
        rstr += ("%s%s: %.0f units (%.0f kg full tank mass)\n" %
                 (f_yes if Features.monopropellant in self.features else f_no,
                  self.fueltype.pname,
                  fueltankmass / (self.get_f_e() + 1) / self.fueltype.unitmass,
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
            if (self.sfbcount != 1 and self.mainengine.tvc > 0.0) and \
                    (a.sfbcount == 1 or a.mainengine.tvc == 0.0):
                return True
        elif bestgimbal >= 2:
            if self.mainengine.tvc > a.mainengine.tvc:
                return True
        # using monopropellant engine might be an advantage
        if prefermonopropellant and \
                (self.fueltype is parts.FuelTypes.Monopropellant) and \
                (a.fueltype is not parts.FuelTypes.Monopropellant):
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
            if self.size is parts.RadialSize.RadiallyMounted and \
                    (a.size is not parts.RadialSize.RadiallyMounted and a.size is not preferredsize):
                return True
        # to be earlier available in the game is an advantage
        if self.requiredscience.is_easier_than(a.requiredscience):
            return True
        if self.get_mass() == a.get_mass() and self.get_cost() == a.get_cost() \
                and sum(self.performance[0]) > sum(a.performance[0]):
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
        if prefermonopropellant and self.fueltype is parts.FuelTypes.Monopropellant:
            self.features.add(Features.monopropellant)
        if prefergenerators and self.mainengine.electricity:
            self.features.add(Features.generator)
        if preferredsize is not None and \
                (self.size is preferredsize or self.size is parts.RadialSize.RadiallyMounted):
            self.features.add(Features.radial_size)


def create_lf_design(payload, pressure, dv, acc, eng,
                     size=None, count=1, fueltype=parts.FuelTypes.LiquidFuel, tank=None):
    """Creates a simple non-SFB design with given parameters

    :type eng: parts.Engine
    :type size: parts.RadialSize
    :type fueltype: parts.FuelTypes
    :type tank: parts.SpecialFuelTank
    """
    if size is None:
        size = eng.size
    design = Design(payload, eng, count, size, fueltype)
    if fueltype is parts.FuelTypes.LiquidFuel:
        f_e = 1 / 8
    elif fueltype is parts.FuelTypes.AtomicFuel:
        f_e = parts.AtomicTank_f_e
    else:
        f_e = tank.f_e
    lf = physics.lf_needed_fuel(dv, physics.engine_isp(eng, pressure), design.get_mass(), f_e)
    if lf is None:
        return None
    if fueltype is parts.FuelTypes.LiquidFuel or fueltype is parts.FuelTypes.AtomicFuel:
        design.add_conventional_tanks((1 + f_e) * lf)
    else:
        design.add_special_tanks((1 + f_e) * lf, tank)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    return design


def create_single_lfe_design(payload, pressure, dv, acc, eng):
    return create_lf_design(payload, pressure, dv, acc, eng)


def create_radial_lfe_design(payload, pressure, dv, acc, eng, size, count):
    return create_lf_design(payload, pressure, dv, acc, eng, size=size, count=count)


def create_atomic_design(payload, pressure, dv, acc):
    return create_lf_design(payload, pressure, dv, acc, parts.AtomicRocketMotor,
                            count=1, fueltype=parts.FuelTypes.AtomicFuel)


def create_xenon_design(payload, pressure, dv, acc, tank):
    size = tank.size if tank.size is not parts.RadialSize.RadiallyMounted else parts.RadialSize.Tiny
    return create_lf_design(payload, pressure, dv, acc, parts.ElectricPropulsionSystem,
                            size=size, fueltype=parts.FuelTypes.Xenon, tank=tank)


def create_monopropellant_design(payload, pressure, dv, acc, tank, count):
    return create_lf_design(payload, pressure, dv, acc, parts.MonoPropellantEngine,
                            size=tank.size, count=count, fueltype=parts.FuelTypes.Monopropellant, tank=tank)


def create_sfb_design(payload, pressure, dv, acc, eng, eng_F_percentage, size, count, sfb, sfbcount):
    """Create LiquidFuel + SFB design with given parameters"""
    design = Design(payload, eng, count, size, parts.FuelTypes.LiquidFuel)
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
    design.add_conventional_tanks(9 / 8 * lf)
    design.calculate_performance(dv, pressure)
    if not design.has_enough_acceleration(acc):
        return None
    if sfbcount != 1:
        design.notes.append("Set liquid fuel engine thrust to {:.0%} while SFB are burning".format(eng_F_percentage))
    return design


def create_single_lfe_sfb_design(payload, pressure, dv, acc, eng, eng_F_percentage, sfb, sfbcount):
    return create_sfb_design(payload, pressure, dv, acc, eng, eng_F_percentage, eng.size, 1, sfb, sfbcount)


def create_radial_lfe_sfb_design(payload, pressure, dv, acc, eng, eng_F_percentage, size, count, sfb, sfbcount):
    return create_sfb_design(payload, pressure, dv, acc, eng, eng_F_percentage, size, count, sfb, sfbcount)


def find_designs(payload, pressure, dv, min_acceleration,
                 preferredsize = None, bestgimbal = 0, sfballowed = False, prefergenerators = False,
                 prefershortengines = False, prefermonopropellant = True):
    # pressure: 0 = vacuum, 1 = kerbin
    designs = []
    d = create_atomic_design(payload, pressure, dv, min_acceleration)
    if d is not None:
        designs.append(d)
    for xetank in parts.XenonTanks:
        d = create_xenon_design(payload, pressure, dv, min_acceleration, xetank)
        if d is not None:
            designs.append(d)
    for mptank in parts.MonoPropellantTanks:
        for count in [2, 3, 4, 6, 8]:
            d = create_monopropellant_design(payload, pressure, dv, min_acceleration,
                                             mptank, count)
            if d is not None:
                designs.append(d)
                break  # do not try more engines as it wouldn't have any advantage
    for eng in parts.LiquidFuelEngines:
        if eng.size is parts.RadialSize.RadiallyMounted:
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
