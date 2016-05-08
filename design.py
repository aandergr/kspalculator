from math import ceil, log
from scipy.optimize import newton

import parts

class Design:
    # TODO: invent better data structure for this thing
    def printinfo(self):
        # TODO: print() is not so good for this
        print("mass: %i kg" % self.mass)
        print("cost: %i" % self.cost)
        print("min_acceleration: %.1f m/s^2" % self.min_acceleration)
        # TODO: print delta v
        print("engine: %s * %i" % (self.eng.name, self.engcount))
        print("fuel: %i kg (tank weight)" % self.fuel)
        print("gimbal: %.1f °" % self.eng.tvc)
        print("%s" % self.size)
        print("%s" % self.eng.level)
        print("IsBest: %r" % self.IsBest)
    def IsBetterThan(self, a, bestgimbal):
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
            if self.eng.tvc > a.eng.tvc:
                return True
        else:
            if self.eng.tvc > 0.0 and a.eng.tvc == 0.0:
                return True
        # check if self uses simpler technology
        if a.eng.level is not self.eng.level and a.eng.level.DependsOn(self.eng.level):
            return True
        return False

def lf_needed_fuel(delta_v, I_sp, m_p):
    def f(m_f):
        return delta_v - (I_sp * 9.81 * log((m_p+m_f+m_f/8)/(m_p+m_f/8)))
    return newton(f, 0)

# TODO: unify design creation

def CreateSingleLFEngineDesign(payload, pressure, dv, eng):
    design = Design()
    design.mass = payload + eng.m
    design.cost = eng.cost
    design.eng = eng
    design.engcount = 1
    design.size = eng.size
    isp = pressure*eng.isp_atm + (1-pressure)*eng.isp_vac
    F = pressure*eng.F_atm + (1-pressure)*eng.F_vac
    lf = lf_needed_fuel(dv, isp, design.mass)
    lf = lf * 9/8
    # we only consider tanks with same radial size as engine.
    smalltankcount = ceil(lf / parts.RocketFuelTanks[parts.SmallestTank[eng.size]].m_full)
    design.fuel = smalltankcount * parts.RocketFuelTanks[parts.SmallestTank[eng.size]].m_full
    design.mass = design.mass + design.fuel
    # Fuel tank calculation:
    # We use that
    # - Tanks get always two times bigger
    # - Bigger tanks are never more expensive
    for i in range(parts.SmallestTank[eng.size], parts.BiggestTank[eng.size]+1):
        if i != parts.BiggestTank[eng.size]:
            if smalltankcount % 2 != 0:
                design.cost = design.cost + parts.RocketFuelTanks[i].cost
            smalltankcount = smalltankcount // 2
        else:
            design.cost = design.cost + smalltankcount * parts.RocketFuelTanks[i].cost
    design.min_acceleration = F / design.mass
    return design

def CreateRadialLFEnginesDesign(payload, pressure, dv, eng, size, count):
    design = Design()
    design.mass = payload + count*eng.m
    design.cost = count*eng.cost
    design.eng = eng
    design.engcount = count
    design.size = size
    isp = pressure*eng.isp_atm + (1-pressure)*eng.isp_vac
    F = count * (pressure*eng.F_atm + (1-pressure)*eng.F_vac)
    lf = lf_needed_fuel(dv, isp, design.mass)
    lf = lf * 9/8
    smalltankcount = ceil(lf / parts.RocketFuelTanks[parts.SmallestTank[size]].m_full)
    design.fuel = smalltankcount * parts.RocketFuelTanks[parts.SmallestTank[size]].m_full
    design.mass = design.mass + design.fuel
    # Fuel tank calculation:
    # We use that
    # - Tanks get always two times bigger
    # - Bigger tanks are never more expensive
    for i in range(parts.SmallestTank[size], parts.BiggestTank[size]+1):
        if i != parts.BiggestTank[size]:
            if smalltankcount % 2 != 0:
                design.cost = design.cost + parts.RocketFuelTanks[i].cost
            smalltankcount = smalltankcount // 2
        else:
            design.cost = design.cost + smalltankcount * parts.RocketFuelTanks[i].cost
    design.min_acceleration = F / design.mass
    return design

# TODO: add ship design with radially mounted liquid fuel engines
# TODO: add ship designs using atomic rocket motor, monopropellant engine, ion engine
# TODO: add ship radially mounted fuel tank + engine combinations
# TODO: add ship design with solid fuel booster

# TODO: consider ship width and adapters

# TODO: support delta-v with different pressure

def FindDesigns(payload, pressure, dv, min_acceleration, bestgimbal = False):
    """
    pressure: 0 = vacuum, 1 = kerbin
    """
    designs = []
    for eng in parts.LiquidFuelEngines:
        if eng.size is parts.RadialSize.RdMntd:
            # TODO: this way Tiny almost always wins, that's not so good
            for size in [parts.RadialSize.Tiny, parts.RadialSize.Small, parts.RadialSize.Large, parts.RadialSize.ExtraLarge]:
                for count in [2, 3, 4, 6, 8]:
                    d = CreateRadialLFEnginesDesign(payload, pressure, dv, eng, size, count)
                    if d.min_acceleration >= min_acceleration:
                        designs.append(d)
                        break   # do not try more engines
        else:
            d = CreateSingleLFEngineDesign(payload, pressure, dv, eng)
            if d.min_acceleration >= min_acceleration:
                designs.append(d)

    for d in designs:
        d.IsBest = True
        for e in designs:
            if (d is not e) and (not d.IsBetterThan(e, bestgimbal)):
                d.IsBest = False
                break

    return designs
