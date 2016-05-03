from math import ceil, log
from scipy.optimize import newton

import parts

class Design:
    # mass, cost, min_acceleration
    # engine
    # fuel
    #
    def printinfo(self):
        print("mass: %i kg" % self.mass)
        print("cost: %i" % self.cost)
        print("min_acceleration: %.1f m/s^2" % self.min_acceleration)
        print("engine: %s" % self.eng.name)
        print("fuel: %i kg (tank weight)" % self.fuel)
        
def lf_needed_fuel(delta_v, I_sp, m_p):
    def f(m_f):
        return delta_v - (I_sp * 9.81 * log((m_p+m_f+m_f/8)/(m_p+m_f/8)))
    return newton(f, 0)

def TryLFEngine(payload, pressure, dv, eng):
    design = Design()
    design.mass = payload + eng.m
    design.cost = eng.cost
    design.eng = eng
    isp = pressure*eng.isp_atm + (1-pressure)*eng.isp_vac
    F = pressure*eng.F_atm + (1-pressure)*eng.F_vac
    lf = lf_needed_fuel(dv, isp, design.mass)
    lf = lf * 9/8
    # TODO: Small!?
    smalltankcount = ceil(lf / parts.RocketFuelTanks[parts.Small_SmallestTank].m_full)
    design.fuel = smalltankcount * parts.RocketFuelTanks[parts.Small_SmallestTank].m_full
    design.mass = design.mass + design.fuel
    for i in range(parts.Small_SmallestTank, parts.Small_BiggestTank+1):
        if i != parts.Small_BiggestTank:
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

    # TODO: remove shit
    # TODO: sort

    return designs
