from math import ceil

import parts
import physics

class Design:
    def __init__(self, payload, mainengine, mainenginecount, size):
        self.mass = payload + mainenginecount*mainengine.m
        self.cost = mainenginecount * mainengine.cost
        self.mainengine = mainengine
        self.mainenginecount = mainenginecount
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
    def AddSFB(self, sfb, sfbcount):
        self.sfb = sfb
        self.sfbcount = sfbcount
        if sfbcount == 1:
            self.sfbmountmass = parts.StackstageExtraMass
            self.cost = self.cost + parts.StackstageExtraCost
            self.notes.append("Vertically stacked %s SFB" % sfb.name)
            self.notes.append("SFB mounted on %s" % parts.StackstageExtraNote)
        else:
            self.sfbmountmass = sfbcount*parts.RadialstageExtraMass
            self.cost = self.cost + sfbcount*parts.RadialstageExtraCost
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
        f_e = self.mainengine.f_e
        tankcount = ceil(xf / parts.XenonTank.m_full)
        self.specialfuel = tankcount * parts.XenonTank.m_full
        self.specialfueltype = "Xenon"
        self.specialfuelunitmass = parts.XenonUnitMass
        self.mass = self.mass + self.specialfuel
        self.cost = self.cost + tankcount*parts.XenonTank.cost
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
            self.performance = physics.sflf_performance(dv,
                    physics.engine_isp(self.mainengine, pressure),
                    physics.engine_isp(self.sfb, pressure),
                    physics.engine_force(self.mainenginecount, self.mainengine, pressure),
                    physics.engine_force(self.sfbcount, self.sfb, pressure),
                    pressure,
                    self.mass - self.liquidfuel - self.sfbmountmass - self.sfbcount*self.sfb.m_full,
                    self.liquidfuel*8/9,
                    self.sfbmountmass,
                    self.sfbcount*self.sfb.m_full,
                    self.sfbcount*self.sfb.m_empty)
    def EnoughAcceleration(self, min_acceleration):
        if self.performance is None:
            return False
        dv, p, a_s, a_t, m_s, m_t, solid, op = self.performance
        for i in range(len(a_s)):
            if a_s[i] < min_acceleration[op[i]]:
                return False
        return True
    def PrintPerformance(self):
        dv, p, a_s, a_t, m_s, m_t, solid, op = self.performance
        for i in range(len(dv)):
            p_str = ("%.2f atm" % p[i]) if p[i] > 0 else "vacuum  "
            solid_str = "*" if solid[i] else " "
            print("\t %s%i:  %4.0f m/s @ %s  %5.2f m/s² - %5.2f m/s²  %5.1f t - %5.1f t" % \
                    (solid_str, i+1, dv[i], p_str, a_s[i], a_t[i], m_s[i]/1000.0, m_t[i]/1000.0))
    def SetSFBLimit(self, pressure, acc):
        dv, p, a_s, a_t, m_s, m_t, solid, op = self.performance
        limit = 0.0
        for i in range(len(a_s)):
            if solid[i] and acc[i]/a_s[i] > limit:
                limit = acc[i]/a_s[i]
        if limit < 0.95:
            self.notes.append("You might limit SFB thrust to %.1f %%" % (ceil(limit*200)/2.0))
    def PrintInfo(self):
        if self.mainenginecount == 1:
            print("%s" % self.mainengine.name)
        else:
            print("%i * %s, radially mounted" % (self.mainenginecount, self.mainengine.name))
        print("\tTotal Mass: %.0f kg (including payload and full tanks)" % self.mass)
        print("\tCost: %.0f" % self.cost)
        if self.liquidfuel is not None:
            print("\tLiquid fuel: %.0f units (%.0f kg full tank mass)" % (self.liquidfuel*8/9*0.2, self.liquidfuel))
        if self.specialfuel is not None:
            print("\t%s: %.0f units (%.0f kg full tank mass)" % \
                    (self.specialfueltype, self.specialfuel/(self.mainengine.f_e+1)/self.specialfuelunitmass,
                        self.specialfuel))
        print("\tGimbal: %.1f °" % self.mainengine.tvc)
        print("\tRadial size: %s" % self.size.name)
        if self.sfb is None:
            req = self.mainengine.level.name
        else:
            if self.sfb.level.DependsOn(self.mainengine.level):
                req = self.sfb.level.name
            elif self.mainengine.level.DependsOn(self.sfb.level):
                req = self.mainengine.level.name
            else:
                req = "%s and %s" % (self.sfb.level.name, self.mainengine.level.name)
        print("\tRequires: %s" % req)
        for n in self.notes:
            print("\t%s" % n)
        print("\tPerformance:")
        self.PrintPerformance()
    def MoreSophisticated(self, a):
        # check if self uses simpler technology than a
        if self.sfb is None and a.sfb is None:
            return a.mainengine.level.MoreSophisticated(self.mainengine.level)
        if self.sfb is None and a.sfb is not None:
            return a.mainengine.level.MoreSophisticated(self.mainengine.level) and \
                    a.sfb.level.MoreSophisticated(self.mainengine.level)
        if self.sfb is not None and a.sfb is None:
            return a.mainengine.level.MoreSophisticated(self.mainengine.level) or \
                    a.mainengine.level.MoreSophisticated(self.sfb.level)
        else:
            return (a.mainengine.level.MoreSophisticated(self.mainengine.level) and \
                    a.sfb.level.MoreSophisticated(self.mainengine.level)) or \
                    (a.mainengine.level.MoreSophisticated(self.sfb.level) and \
                    a.sfb.level.MoreSophisticated(self.sfb.level))
    def IsBetterThan(self, a, preferredsize, bestgimbal):
        """
        Returns True if self is better than a by any parameter, i.e. there might
        be a reason to use self instead of a.
        """
        # obvious and easy to check criteria
        if (self.mass < a.mass) or (self.cost < a.cost):
            return True
        # check if we have better gimbal
        if bestgimbal:
            if self.mainengine.tvc > a.mainengine.tvc:
                return True
        else:
            if self.mainengine.tvc > 0.0 and a.mainengine.tvc == 0.0:
                return True
        # this is where user's size preferrence comes in
        if preferredsize is not None:
            if self.size is preferredsize and a.size is not preferredsize:
                return True
        if a.MoreSophisticated(self):
            return True
        return False

# TODO: simplify design creation even more. Overthink class Design and whole design.py

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

def CreateSingleLFESFBDesign(payload, pressure, dv, acc, eng, sfb, sfbcount):
    design = Design(payload, eng, 1, eng.size)
    design.AddSFB(sfb, sfbcount)
    lf = physics.sflf_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.mass - design.sfbmountmass - sfbcount*sfb.m_full,
            design.sfbmountmass, sfbcount*sfb.m_full, sfbcount*sfb.m_empty)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    design.SetSFBLimit(pressure, acc)
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

def CreateRadialLFESFBDesign(payload, pressure, dv, acc, eng, size, count, sfb, sfbcount):
    design = Design(payload, eng, count, size)
    design.AddSFB(sfb, sfbcount)
    lf = physics.sflf_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.mass - design.sfbmountmass - sfbcount*sfb.m_full,
            design.sfbmountmass, sfbcount*sfb.m_full, sfbcount*sfb.m_empty)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculatePerformance(dv, pressure)
    if not design.EnoughAcceleration(acc):
        return None
    design.SetSFBLimit(pressure, acc)
    return design

# TODO: add ship radially mounted fuel tank + engine combinations
# TODO: add asparagous designs

def FindDesigns(payload, pressure, dv, min_acceleration,
        preferredsize = None, bestgimbal = False, sfballowed = False):
    # pressure: 0 = vacuum, 1 = kerbin
    designs = []
    d = CreateAtomicRocketMotorDesign(payload, pressure, dv, min_acceleration)
    if d is not None:
        designs.append(d)
    d = CreateElectricPropulsionSystemDesign(payload, pressure, dv, min_acceleration)
    if d is not None:
        designs.append(d)
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
                                d = CreateRadialLFESFBDesign(payload, pressure, dv, min_acceleration,
                                        eng, size, count, sfb, sfbcount)
                                if d is not None:
                                    designs.append(d)
        else:
            d = CreateSingleLFEngineDesign(payload, pressure, dv, min_acceleration, eng)
            if d is not None:
                designs.append(d)
            if sfballowed and eng.size is not parts.RadialSize.Tiny:
                for sfbcount in [1, 2, 3, 4, 6, 8]:
                    if sfbcount == 1 and size is not parts.RadialSize.Small:
                        # would look bad
                        continue
                    for sfb in parts.SolidFuelBoosters:
                        d = CreateSingleLFESFBDesign(payload, pressure, dv, min_acceleration,
                                eng, sfb, sfbcount)
                        if d is not None:
                            designs.append(d)

    for d in designs:
        d.IsBest = True
        for e in designs:
            if (d is not e) and (not d.IsBetterThan(e, preferredsize, bestgimbal)):
                d.IsBest = False
                break

    return designs
