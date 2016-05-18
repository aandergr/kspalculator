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

def lf_needed_fuel(dv, I_sp, m_p):
    f_e = 1/8   # empty weight fraction
    m_c = m_p/f_e * ((1/f_e) / (1+(1/f_e)-exp(1/g_0*fsum([dv[i]/I_sp[i] for i in range(len(dv))]))) - 1)
    if m_c < 0:
        warn("negative m_c occured in lf_needed_fuel()")
        return None
    return m_c

def lf_performance(dv, I_sp, F, p, m_p, m_c):
    f_e = 1/8   # empty weight fraction
    def l(Isp, m_s, m_t):
        return g_0 * Isp * log((m_p + f_e*m_c + m_s) / (m_p + f_e*m_c + m_t))
    def equations(x):
        dvn = x[0]
        m = x
        n = len(m)-1
        y = len(m)*[0]
        # case n=0 does not exist, as we have at least two phases including
        # extra phase.
        if n == 1:
            y[0] = l(I_sp[0], m_c, m[1]) - dv[0]
            y[1] = l(I_sp[1], m[1], 0) - dvn
        else:
            y[0] = l(I_sp[0], m_c, m[1]) - dv[0]
            for i in range(1,n):
                y[i] = l(I_sp[i], m[i], m[i+1]) - dv[i]
            y[n] = l(I_sp[n], m[n], 0) - dvn
        return y
    n = len(dv)-1
    # this is to put extra in extra phase
    dv = dv + [0]
    I_sp = I_sp + [I_sp[n]]
    F = F + [F[n]]
    p = p + [p[n]]
    n = n + 1
    # call the solver
    x0 = [dv[n]] + n*[0]
    sol = fsolve(equations, x0)
    # evaluate solution
    r_dv = [dv[i] for i in range(n)] + [sol[0]]
    r_p = p
    r_solid = (n+1)*[False]
    r_m_s = [m_p + f_e*m_c + m_c] + \
            [m_p + f_e*m_c + sol[i] for i in range(1,n+1)]
    r_m_t = [m_p + f_e*m_c + sol[i] for i in range(1,n+1)] + \
            [m_p + f_e*m_c]
    r_a_s = [F[i] / r_m_s[i] for i in range(n+1)]
    r_a_t = [F[i] / r_m_t[i] for i in range(n+1)]
    r_op = [i for i in range(n)] + [n-1]
    return r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op

def sflf_needed_fuel(dv, I_spl, I_sps, m_p, m_x, sm_s, sm_t):
    def equations(m, *args):
        def s(Isp, m_s, m_t, m_c):
            return g_0 * Isp * log((m_p + 9/8*m_c + m_x + m_s) / (m_p + 9/8*m_c + m_x + m_t))
        def l(Isp, m_s, m_t, m_c):
            return g_0 * Isp * log((m_p + 1/8*m_c + m_s) / (m_p + 1/8*m_c + m_t))
        lfe_phase, = args
        n = len(m)-1
        y = []  # TODO: preallocate this
        for i in range(n):
            if i == 0:
                if lfe_phase > 0:
                    y.append(s(I_sps[0], sm_s, m[1], m[0]) - dv[0])
                else:
                    y.append(s(I_sps[0], sm_s, sm_t, m[0]) + l(I_spl[0], m[0], m[1], m[0]) - dv[0])
            else:
                if lfe_phase > i:
                    y.append(s(I_sps[i], m[i], m[i+1], m[0]) - dv[i])
                elif lfe_phase < i:
                    y.append(l(I_spl[i], m[i], m[i+1], m[0]) - dv[i])
                else:
                    y.append(s(I_sps[i], m[i], sm_t, m[0]) + l(I_spl[i], m[0], m[i+1], m[0]) - dv[i])
        if lfe_phase < n:
            y.append(l(I_spl[n], m[n], 0, m[0]) - dv[n])
        else:
            s_ig = sm_s if n == 0 else m[n]
            y.append(s(I_sps[n], s_ig, sm_t, m[0]) + l(I_spl[n], m[0], 0, m[0]) - dv[n])
        return y
    for lfe_phase in range(len(dv)-1, -1, -1):
        try:
            (sol, infodict, ier, mesg) = fsolve(equations, [0 for i in range(len(I_spl))],
                    full_output=True, args=lfe_phase)
        except ValueError:
            continue
        if ier:
            if min(sol) < 0:
                # in this case no warning. only means that SFBs were too strong
                return None
            return sol[0]
    return None

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
