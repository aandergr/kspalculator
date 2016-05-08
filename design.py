from math import ceil, log
from scipy.optimize import newton

import parts

class Design:
    def printinfo(self):
        # TODO: print() is not so good for this
        print("mass: %i kg" % self.mass)
        print("cost: %i" % self.cost)
        print("min_acceleration: %.1f m/s^2" % self.min_acceleration)
        print("engine: %s" % self.eng.name)
        print("fuel: %i kg (tank weight)" % self.fuel)
        print("gimbal: %.1f °" % self.eng.tvc)
        print("%s" % self.size)
        print("%s" % self.eng.level)
        print("IsBest: %r" % self.IsBest)
    def IsBetterThan(self, a):
        """
        Returns True if self is better than a by any parameter, i.e. there might
        be a reason to use self instead of a.
        """
        # obvious and easy to check criteria
        if  (self.mass < a.mass) or \
            (self.cost < a.cost) or \
            (self.eng.tvc > a.eng.tvc):
            return True
        # min_acceleration is not a good criteria, as a higher acceleration than
        # the minimum required acceleration is usually not useful
        # check if self uses simpler technology
        if a.eng.level is not self.eng.level and a.eng.level.DependsOn(self.eng.level):
            return True
        return False

def lf_needed_fuel(delta_v, I_sp, m_p):
    def f(m_f):
        return delta_v - (I_sp * 9.81 * log((m_p+m_f+m_f/8)/(m_p+m_f/8)))
    return newton(f, 0)

def TryLFEngine(payload, pressure, dv, eng):
    design = Design()
    design.mass = payload + eng.m
    design.cost = eng.cost
    design.eng = eng
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

# TODO: add other ship designs

def FindDesigns(payload, pressure, dv, min_acceleration):
    """
    pressure: 0 = vacuum, 1 = kerbin
    """
    designs = []
    for eng in parts.LiquidFuelEngines:
        d = TryLFEngine(payload, pressure, dv, eng)
        if d.min_acceleration >= min_acceleration:
            designs.append(d)

    for d in designs:
        d.IsBest = True
        for e in designs:
            if (d is not e) and (not d.IsBetterThan(e)):
                d.IsBest = False
                break

    return designs
