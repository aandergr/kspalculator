# Python 2.7 support.
from __future__ import division

from math import log, exp, fsum

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

# some formulations of the rocket equation
def g_m_t(m_s, dv, I_sp):
    return m_s * exp(-dv/(I_sp*g_0))
def g_dv(m_s, m_t, I_sp):
    return g_0 * I_sp * log(m_s/m_t)
def dv_s(Isp, m_s, m_t, m_p, m_x, m_c):
    return g_0 * Isp * log((m_p + 9/8*m_c + m_x + m_s) / (m_p + 9/8*m_c + m_x + m_t))
def dv_l(Isp, m_s, m_t, m_p, m_c):
    return g_0 * Isp * log((m_p + 1/8*m_c + m_s) / (m_p + 1/8*m_c + m_t))

def lf_needed_fuel(dv, I_sp, m_p, f_e):
    m_c = m_p/f_e * ((1/f_e) / (1+(1/f_e)-exp(1/g_0*fsum([dv[i]/I_sp[i] for i in range(len(dv))]))) - 1)
    if m_c < 0:
        return None
    return m_c

def lf_performance(dv, I_sp, F, p, m_p, m_c, f_e):
    n = len(dv)
    r_m_s = [m_p + f_e*m_c + m_c] + n*[None]
    for i in range(1,n+1):
        r_m_s[i] = g_m_t(r_m_s[i-1], dv[i-1], I_sp[i-1])
    r_m_t = r_m_s[1:] + [m_p + f_e*m_c]
    r_dv = dv + [g_dv(r_m_s[n], r_m_t[n], I_sp[n-1])]
    r_p = p + [p[n-1]]
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
            for i in range(f-1,-1,-1):
                if f_limits[i] >= mc:
                    return i+1
            return 0
    f = f_adjust(0,0)
    precision = 0.001
    def mc_improve(mc_old):
        m_f = exp(-fsum([dv[k]/I_sps[k] for k in range(0,f)])/g_0)
        m_f = sm_s*m_f+(m_f-1)*(m_p+9/8*mc_old+m_x)
        return lf_needed_fuel([dv[f]-s(I_sps[f],m_f,sm_t,mc_old)]+dv[f+1:n+1], I_spl[f:n+1], m_p, 1/8)
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

def sflf_concurrent_needed_fuel(dv, I_spl, I_sps, m_p, m_x, sm_s, sm_t, lpsr):
    # lpsr: liquid-per-solid-ratio = Fl * I_sps / Fs / I_spl
    # I_sph: Specific impulse of the combined engine when liquid and solid fuel burns simultaneously
    I_sph = [(I_spl[k] * lpsr + I_sps[k]) / (1 + lpsr) for k in range(len(I_sps))]
    mc_extra = (sm_s - sm_t) * lpsr
    fuel = sflf_needed_fuel(dv, I_spl, I_sph, m_p + mc_extra * 1/8, m_x, sm_s + mc_extra, sm_t)
    if fuel is not None:
        return mc_extra + fuel

def sflf_performance(dv, I_spl, I_sps, Fl, Fs, p, m_p, m_c, m_x, sm_s, sm_t):
    n = len(dv)
    r_m_t = (n+2)*[None]
    r_m_s = [m_p + 9/8*m_c + m_x + sm_s] + (n+1)*[None]
    r_op = (n+2)*[None]
    r_solid = (n+2)*[None]
    r_dv = (n+2)*[None]
    # sfb only phases
    i = 0
    while g_dv(r_m_s[i], m_p + 9/8*m_c + m_x + sm_t, I_sps[i]) >= dv[i]:
        r_m_t[i] = g_m_t(r_m_s[i], dv[i], I_sps[i])
        r_m_s[i+1] = r_m_t[i]
        r_dv[i] = g_dv(r_m_s[i], r_m_t[i], I_sps[i])   # inefficient, but double-checking
        r_solid[i] = True
        r_op[i] = i
        i = i+1
    # sfb + lfe phase
    r_m_t[i] = m_p + 9/8*m_c + m_x + sm_t
    r_dv[i] = g_dv(r_m_s[i], r_m_t[i], I_sps[i])
    r_solid[i] = True
    r_op[i] = i
    r_m_s[i+1] = m_p + 9/8*m_c
    r_dv[i+1] = dv[i] - r_dv[i]
    r_m_t[i+1] = g_m_t(r_m_s[i+1], r_dv[i+1], I_spl[i])
    r_solid[i+1] = False
    r_op[i+1] = i
    # lfe only phases
    for j in range(i+2, n+2):
        # Why'd you have to go and make things so complicated?...
        r_m_s[j] = r_m_t[j-1]
        r_op[j] = j-1 if j != n+1 else j-2
        r_solid[j] = False
        r_m_t[j] = g_m_t(r_m_s[j], dv[j-1], I_spl[j-1]) if j != n+1 else \
                m_p + 1/8*m_c
        r_dv[j] = g_dv(r_m_s[j], r_m_t[j], I_spl[r_op[j]])   # inefficient, but double-checking
    r_a_s = [(Fs[r_op[j]] if r_solid[j] else Fl[r_op[j]])/r_m_s[j] for j in range(n+2)]
    r_a_t = [(Fs[r_op[j]] if r_solid[j] else Fl[r_op[j]])/r_m_t[j] for j in range(n+2)]
    r_p = [p[r_op[j]] for j in range(n+2)]
    return r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op

def sflf_concurrent_performance(dv, I_spl, I_sps, Fl, Fs, p, m_p, m_c, m_x, sm_s, sm_t, LFE_limit):
    lpsr = LFE_limit * Fl[0] * I_sps[0] / Fs[0] / I_spl[0]
    I_sph = [(I_spl[k] * lpsr + I_sps[k]) / (1 + lpsr) for k in range(len(I_sps))]
    mc_extra = (sm_s - sm_t) * lpsr
    return sflf_performance(dv, I_spl, I_sph, Fl,
                            [Fs[k] + Fl[k] * LFE_limit for k in range(len(Fl))],
                            p, m_p + 1/8 * mc_extra, m_c - mc_extra, m_x, sm_s + mc_extra, sm_t)

def engine_isp(eng, pressure):
    return [pressure[i]*eng.isp_atm + (1-pressure[i])*eng.isp_vac for i in range(len(pressure))]

def engine_force(count, eng, pressure):
    return [count*(pressure[i]*eng.F_vac*eng.isp_atm/eng.isp_vac + (1-pressure[i])*eng.F_vac)
            for i in range(len(pressure))]
