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
        self.min_acceleration = 0
        self.fuel = 0
        self.notes = []
        self.sfb = None
        self.sfbcount = 0
        self.sfbmountmass = 0
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
        """lf should be full tank mass"""
        smalltankcount = ceil(lf / parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full)
        self.fuel = smalltankcount * parts.RocketFuelTanks[parts.SmallestTank[self.size]].m_full
        self.mass = self.mass + self.fuel
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
    def CalculateMinAcceleration(self, pressure):
        # TODO: let this be the minimum over the complete acceleration path
        # TODO (rework this)
        if self.sfb is None:
            F = self.mainenginecount * physics.engine_force(self.mainengine, pressure)
            self.min_acceleration = F / self.mass
        else:
            A_l = self.mainenginecount * physics.engine_force(self.mainengine, pressure) / \
                    (self.mass - self.sfbmountmass - self.sfbcount*self.sfb.m_full)
            A_s = self.sfbcount * physics.engine_force(self.sfb, pressure) / self.mass
            self.min_acceleration = min(A_l, A_s)
    def SetSFBLimit(self, pressure, min_accel):
        A_s = self.sfbcount * physics.engine_force(self.sfb, pressure) / self.mass
        self.notes.append("You might limit SFB thrust to %i %%" % ceil(min_accel/A_s*100))
    def printinfo(self):
        if self.mainenginecount == 1:
            print("%s" % self.mainengine.name)
        else:
            print("%i * %s, radially mounted" % (self.mainenginecount, self.mainengine.name))
        print("\tTotal Mass: %i kg (including payload and full tanks)" % self.mass)
        print("\tCost: %i" % self.cost)
        print("\tMin. acceleration: %.1f m/s²" % self.min_acceleration)
        print("\tLiquid fuel: %i units (%i kg full tank mass)" % (self.fuel*8/9*0.2, self.fuel))
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
        # min_acceleration is not a good criteria, as a higher acceleration than
        # the minimum required acceleration is usually not useful
        # check if we have better gimbal
        if bestgimbal:
            if self.mainengine.tvc > a.mainengine.tvc:
                return True
        else:
            if self.mainengine.tvc > 0.0 and a.mainengine.tvc == 0.0:
                return True
        # TODO: radially mounted engines might be an advantage
        # this is where user's size preferrence comes in
        if preferredsize is not None:
            if self.size is preferredsize and a.size is not preferredsize:
                return True
        if a.MoreSophisticated(self):
            return True
        return False

# TODO: simplify design creation even more

# TODO: have more options regarding radial size

def CreateSingleLFEngineDesign(payload, pressure, dv, eng):
    design = Design(payload, eng, 1, eng.size)
    lf = physics.lf_needed_fuel(dv, physics.engine_isp(eng, pressure), design.mass)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculateMinAcceleration(pressure)
    return design

def CreateSingleLFESFBDesign(payload, pressure, dv, eng, sfb, sfbcount, min_accel):
    design = Design(payload, eng, 1, eng.size)
    design.AddSFB(sfb, sfbcount)
    lf = physics.sflf_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.mass - design.sfbmountmass - sfbcount*sfb.m_full,
            design.sfbmountmass, sfbcount*sfb.m_full, sfbcount*sfb.m_empty)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculateMinAcceleration(pressure)
    design.SetSFBLimit(pressure, min_accel)
    return design

def CreateRadialLFEnginesDesign(payload, pressure, dv, eng, size, count):
    design = Design(payload, eng, count, size)
    lf = physics.lf_needed_fuel(dv, physics.engine_isp(eng, pressure), design.mass)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculateMinAcceleration(pressure)
    return design

def CreateRadialLFESFBDesign(payload, pressure, dv, eng, size, count, sfb, sfbcount, min_accel):
    design = Design(payload, eng, count, size)
    design.AddSFB(sfb, sfbcount)
    lf = physics.sflf_needed_fuel(dv, physics.engine_isp(eng, pressure),
            physics.engine_isp(sfb, pressure),
            design.mass - design.sfbmountmass - sfbcount*sfb.m_full,
            design.sfbmountmass, sfbcount*sfb.m_full, sfbcount*sfb.m_empty)
    if lf is None:
        return None
    design.AddLiquidFuelTanks(9/8 * lf)
    design.CalculateMinAcceleration(pressure)
    design.SetSFBLimit(pressure, min_accel)
    return design

# TODO: add ship designs using atomic rocket motor, monopropellant engine, ion engine
# TODO: add ship radially mounted fuel tank + engine combinations
# TODO: add asparagous designs

# TODO: consider ship width and adapters
# TODO: consider bi-couplers, tri-couplers, etc.

def FindDesigns(payload, pressure, dv, min_acceleration, preferredsize = None, bestgimbal = False, sfballowed = False):
    """
    pressure: 0 = vacuum, 1 = kerbin
    """
    designs = []
    for eng in parts.LiquidFuelEngines:
        if eng.size is parts.RadialSize.RdMntd:
            for size in [parts.RadialSize.Tiny, parts.RadialSize.Small, parts.RadialSize.Large, parts.RadialSize.ExtraLarge]:
                for count in [2, 3, 4, 6, 8]:
                    d = CreateRadialLFEnginesDesign(payload, pressure, dv, eng, size, count)
                    if d is not None and d.min_acceleration >= min_acceleration:
                        designs.append(d)
                        break   # do not try more engines
                    if sfballowed and size is not parts.RadialSize.Tiny:
                        for sfbcount in [1, 2, 3, 4, 6, 8]:
                            if sfbcount == 1 and size is not parts.RadialSize.Small:
                                # would look bad
                                continue
                            for sfb in parts.SolidFuelBoosters:
                                d = CreateRadialLFESFBDesign(payload, pressure, dv, eng, size, count, sfb, sfbcount, min_acceleration)
                                if d is not None and d.min_acceleration >= min_acceleration:
                                    designs.append(d)
        else:
            d = CreateSingleLFEngineDesign(payload, pressure, dv, eng)
            if d is not None and d.min_acceleration >= min_acceleration:
                designs.append(d)
            if sfballowed and eng.size is not parts.RadialSize.Tiny:
                for sfbcount in [1, 2, 3, 4, 6, 8]:
                    if sfbcount == 1 and size is not parts.RadialSize.Small:
                        # would look bad
                        continue
                    for sfb in parts.SolidFuelBoosters:
                        d = CreateSingleLFESFBDesign(payload, pressure, dv, eng, sfb, sfbcount, min_acceleration)
                        if d is not None and d.min_acceleration >= min_acceleration:
                            designs.append(d)

    for d in designs:
        d.IsBest = True
        for e in designs:
            if (d is not e) and (not d.IsBetterThan(e, preferredsize, bestgimbal)):
                d.IsBest = False
                break

    return designs
