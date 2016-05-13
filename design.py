from math import ceil, log
from scipy.optimize import fsolve

import parts

class Design:
    def __init__(self, payload, mainengine, mainenginecount, size):
        self.mass = payload + mainenginecount*mainengine.m
        self.cost = mainenginecount * mainengine.cost
        self.mainengine = mainengine
        self.mainenginecount = mainenginecount
        self.size = size
        self.min_acceleration = 0
        self.fuel = 0
    def AddLiquidFuelTanks(self, lf):
        """lf should be full tank weight"""
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
        F = self.mainenginecount * engine_force(self.mainengine, pressure)
        self.min_acceleration = F / self.mass
    def printinfo(self):
        if self.mainenginecount == 1:
            print("%s" % self.mainengine.name)
        else:
            print("%i * %s, radially mounted" % (self.mainenginecount, self.mainengine.name))
        print("\ttotal mass: %i kg (including payload)" % self.mass)
        print("\tcost: %i" % self.cost)
        print("\tmin_acceleration: %.1f m/s^2" % self.min_acceleration)
        # TODO: print delta v
        print("\tfuel: %i units (%i kg full tank weight)" % (self.fuel*8/9*0.2, self.fuel))
        print("\tgimbal: %.1f °" % self.mainengine.tvc)
        print("\t%s" % self.size)
        print("\t%s" % self.mainengine.level)
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
        # this is where user's size preferrence comes in
        if preferredsize is not None:
            if self.size is preferredsize and a.size is not preferredsize:
                return True
        # check if self uses simpler technology
        if a.mainengine.level is not self.mainengine.level and a.mainengine.level.DependsOn(self.mainengine.level):
            return True
        return False

def lf_needed_fuel(dv, I_sp, m_p):
    """Returns required fuel weight"""
    g_0 = 9.81
    f_e = 1/8   # empty weight fraction
    def equations(m):
        N = len(m)
        y =     [I_sp[i] * g_0 * log((m_p + m[0]*f_e + m[i])/(m_p + m[0]*f_e + m[i+1])) - dv[i] for i in range(N-1)]
        y.append(I_sp[N-1]*g_0 * log((m_p + m[0]*f_e + m[N-1])/(m_p+m[0]*f_e)) - dv[N-1])
        return y
    sol = fsolve(equations, [0 for i in range(len(I_sp))])
    return sol[0]

def engine_isp(eng, pressure):
    return [pressure[i]*eng.isp_atm + (1-pressure[i])*eng.isp_vac for i in range(len(pressure))]

def engine_force(eng, pressure):
    return pressure[0]*eng.F_atm + (1-pressure[0])*eng.F_vac

# TODO: simplify design creation even more

def CreateSingleLFEngineDesign(payload, pressure, dv, eng):
    # TODO: have more options regarding radial size
    design = Design(payload, eng, 1, eng.size)
    design.AddLiquidFuelTanks(9/8 * lf_needed_fuel(dv, engine_isp(eng, pressure), design.mass))
    design.CalculateMinAcceleration(pressure)
    return design

def CreateRadialLFEnginesDesign(payload, pressure, dv, eng, size, count):
    design = Design(payload, eng, count, size)
    design.AddLiquidFuelTanks(9/8 * lf_needed_fuel(dv, engine_isp(eng, pressure), design.mass))
    design.CalculateMinAcceleration(pressure)
    return design

# TODO: add ship designs using atomic rocket motor, monopropellant engine, ion engine
# TODO: add ship radially mounted fuel tank + engine combinations
# TODO: add ship design with solid fuel booster
# TODO: add asparagous designs

# TODO: consider ship width and adapters

def FindDesigns(payload, pressure, dv, min_acceleration, preferredsize = None, bestgimbal = False):
    """
    pressure: 0 = vacuum, 1 = kerbin
    """
    designs = []
    for eng in parts.LiquidFuelEngines:
        if eng.size is parts.RadialSize.RdMntd:
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
            if (d is not e) and (not d.IsBetterThan(e, preferredsize, bestgimbal)):
                d.IsBest = False
                break

    return designs
