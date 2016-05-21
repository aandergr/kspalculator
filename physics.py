from math import log, exp, fsum
from scipy.optimize import fsolve
from warnings import warn

# *_needed_fuel() functions return needed kilograms of liquid combustible for
# given
#  - dv:    Array of required delta v for each flight phase,
#  - I_sp (or I_spl, I_sps):
#           Array of specific impulse of used engines,
#  - m_p:   Payload, including mass of liquid fuel engine,
#  - m_x:   Extra weight needed to mount solid fuel boosters,
#  - sm_s:  Solid fuel booster start (full) mass,
#  - sm_t:  Solid fuel booster terminal (empty) mass.

# *_performance() functions return a tuple of
#  - dv:    Array of delta v for each flight phase, extraneous dv being added to
#           extra phase,
#  - p:     Pressure used for calculation for each flight phase (This is not
#           actually used for calculation. Given Isp and F are used. We return
#           it as it might be of interest for user),
#  - a_s:   Maximum (full thrust) acceleration at start of each phase,
#  - a_t:   Maximum (full thrust) acceleration at end of each phase,
#  - m_s:   Total mass at start of each phase,
#  - m_t:   Total mass at end of each phase,
#  - solid: Array of whether solid fuel boosters are used in each phase,
#  - op:    Original phase (phases are splitted up when LFE ignites).
# for given
#  - dv:    Array of required delta v for each flight phase,
#  - I_sp (or I_spl, I_sps):
#           Array of specific impulse of used engines,
#  - F (or Fl, Fs):
#           Array of force of used engines,
#  - p:     Array of pressure at each phase (This is not evaluated. Only I_sp
#           and F are used for calculation),
#  - m_p:   Payload, including mass of liquid fuel engine,
#  - m_c:   Mass of liquid combustible carried at start,
#  - m_x:   Extra weight needed to mount solid fuel boosters,
#  - sm_s:  Solid fuel booster start (full) mass,
#  - sm_t:  Solid fuel booster terminal (empty) mass.

# only used for I_sp conversion
g_0 = 9.80665

# TODO: either use them in all places where possible or remove them from global namespace
def dv_s(Isp, m_s, m_t, m_p, m_x, m_c):
    return g_0 * Isp * log((m_p + 9/8*m_c + m_x + m_s) / (m_p + 9/8*m_c + m_x + m_t))
def dv_l(Isp, m_s, m_t, m_p, m_c):
    return g_0 * Isp * log((m_p + 1/8*m_c + m_s) / (m_p + 1/8*m_c + m_t))

def lf_needed_fuel(dv, I_sp, m_p):
    f_e = 1/8   # empty weight fraction
    m_c = m_p/f_e * ((1/f_e) / (1+(1/f_e)-exp(1/g_0*fsum([dv[i]/I_sp[i] for i in range(len(dv))]))) - 1)
    if m_c < 0:
        warn("negative m_c occured in lf_needed_fuel()")
        return None
    return m_c

def lf_performance(dv, I_sp, F, p, m_p, m_c):
    f_e = 1/8   # empty weight fraction
    def m_t(m_s, dv, I_sp):
        return m_s * exp(-dv/(I_sp*g_0))
    def dvl(m_s, m_t, I_sp):
        return g_0 * I_sp * log(m_s/m_t)
    n = len(dv)
    r_m_s = [m_p + f_e*m_c + m_c] + n*[None]
    for i in range(1,n+1):
        r_m_s[i] = m_t(r_m_s[i-1], dv[i-1], I_sp[i-1])
    r_m_t = r_m_s[1:] + [m_p + f_e*m_c]
    r_dv = dv + [dvl(r_m_s[n], r_m_t[n], I_sp[n-1])]
    r_p = p + [0]
    r_solid = (n+1)*[False]
    r_a_s = [F[i if i != n else i-1] / r_m_s[i] for i in range(n+1)]
    r_a_t = [F[i if i != n else i-1] / r_m_t[i] for i in range(n+1)]
    r_op = list(range(n)) + [n-1]
    return r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op

def sflf_needed_fuel(dv, I_spl, I_sps, m_p, m_x, sm_s, sm_t):
    def s(Isp, m_s, m_t, m_c):
        return dv_s(Isp, m_s, m_t, m_p, m_x, m_c)
    n = len(dv)-1
    f_limits = (n+1) * [None]
    def mc_solid(i):
        return ((sm_s-sm_t)/(exp(fsum([dv[k]/I_sps[k] for k in range(0,i+1)])/g_0)-1)-m_p-sm_t-m_x)*8/9
    for i in range(n+1):
        f_limits[i] = mc_solid(i)
        if f_limits[i] < 0:
            f_limits[i+1 : n+1] = (n-i) * [-1]
            break
    else:
        # SFBs are too strong
        return None
    def f_adjust(mc, d):
        if d<=0:
            for i in range(0 if d==0 else f,n+1):
                if f_limits[i] < mc:
                    return i
        else:
            if f == 0:
                return 0
            for i in range(f-1,-1,-1):
                if f_limits[i] >= mc:
                    return i+1
    f = f_adjust(0,0)
    precision = 0.001
    def mc_improve(mc_old):
        return lf_needed_fuel([fsum(dv[0:f+1])-s(fsum(I_sps[0:f+1]),sm_s,sm_t,mc_old)]+ \
            dv[f+1:n+1], I_spl[f:n+2], m_p)
    m_c = 2 * [None]
    current = 1
    m_c[0] = mc_improve(0)
    if m_c[0] is None:
            return None
    f = f_adjust(m_c[0],1)
    while True:
        m_c[current] = mc_improve(m_c[(current+1)%2])
        if m_c[current] is None:
            return None
        if m_c[current] - m_c[(current+1)%2] < precision:
            return m_c[current]
        f = f_adjust(m_c[current],1)
        current = (current+1)%2


def sflf_performance(dv, I_spl, I_sps, Fl, Fs, p, m_p, m_c, m_x, sm_s, sm_t):
    def s(Isp, m_s, m_t):
        return g_0 * Isp * log((m_p + 9/8*m_c + m_x + m_s) / (m_p + 9/8*m_c + m_x + m_t))
    def l(Isp, m_s, m_t):
        return g_0 * Isp * log((m_p + 1/8*m_c + m_s) / (m_p + 1/8*m_c + m_t))
    n = len(dv)-1
    if n == 0:
        dv_s = s(I_sps[0], sm_s, sm_t)
        if (dv_s > dv[0] or l(I_spl[0], m_c, 0) + dv_s < dv[0]):
            # TODO: investigate and fix this
            print("sflf_performance() got very bad input.")
            print(dv, I_spl, I_sps, Fl, Fs, p, m_p, m_c, m_x, sm_s, sm_t)
            print(dv_s, l(I_spl[0], m_c, 0))
            return None
        def equations(x):
            dv_x, m_1 = x
            return [ dv[0] - dv_s - l(I_spl[0], m_c, m_1),
                    dv_x - l(I_spl[0], m_1, 0) ]
        x0 = [0, 0]
        s = fsolve(equations, x0)
        dv_x, m_1 = s
        # return
        r_dv = [dv_s, dv[0] - dv_s, dv_x]
        r_op = [0, 0, 0]
        r_p = 3*[p[0]]
        r_solid = [True, False, False]
        r_m_s = [m_p + 9/8*m_c + m_x + sm_s, \
                 m_p + 1/8*m_c + m_c,
                 m_p + 1/8*m_c + m_1]
        r_m_t = [m_p + 9/8*m_c + m_x + sm_t, \
                 m_p + 1/8*m_c + m_1,
                 m_p + 1/8*m_c]
        r_a_s = [Fs[0] / r_m_s[0], Fl[0] / r_m_s[1], Fl[0] / r_m_s[2]]
        r_a_t = [Fs[0] / r_m_t[0], Fl[0] / r_m_t[1], Fl[0] / r_m_t[2]]
        return r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op
    else:
        # TODO
        raise Exception("Not implemented yet. Use only 1 phase if boosters are allowed.")

def engine_isp(eng, pressure):
    return [pressure[i]*eng.isp_atm + (1-pressure[i])*eng.isp_vac for i in range(len(pressure))]

def engine_force(count, eng, pressure):
    return [count*(pressure[i]*eng.F_vac*eng.isp_atm/eng.isp_vac + (1-pressure[i])*eng.F_vac)
            for i in range(len(pressure))]
