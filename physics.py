from math import log
from scipy.optimize import fsolve

# TODO: have debugging log for *_needed_fuel() functions, keep acceleration path

def lf_needed_fuel(dv, I_sp, m_p):
    """Returns required fuel weight"""
    g_0 = 9.81
    f_e = 1/8   # empty weight fraction
    def equations(m):
        N = len(m)
        y =     [I_sp[i] * g_0 * log((m_p + m[0]*f_e + m[i])/(m_p + m[0]*f_e + m[i+1])) - dv[i] for i in range(N-1)]
        y.append(I_sp[N-1]*g_0 * log((m_p + m[0]*f_e + m[N-1])/(m_p+m[0]*f_e)) - dv[N-1])
        return y
    (sol, infodict, ier, mesg) = fsolve(equations, [0 for i in range(len(I_sp))], full_output=True)
    if not ier:
        return None
    return sol[0]

def sflf_needed_fuel(dv, I_spl, I_sps, m_p, m_x, sm_s, sm_t):
    g_0 = 9.81
    def equations(m):
        def s(Isp, m_s, m_t, m_c):
            return g_0 * Isp * log((m_p + 9/8*m_c + m_x + m_s) / (m_p + 9/8*m_c + m_x + m_t))
        def l(Isp, m_s, m_t, m_c):
            return g_0 * Isp * log((m_p + 1/8*m_c + m_s) / (m_p + 1/8*m_c + m_t))
        n = len(m)-1
        y = []
        f = [ 1 ]   # f[i] = does SFB burn in step i?
        # TODO: use more efficient data structure for f
        for i in range(n):
            if i == 0:
                # Start (but not end) of stage. SFB must be ignited. We distinguish two cases:
                # 1. SFB has enough fuel for this whole step
                # 2. SFB will stop burning this step, LFE will be ignited
                if s(I_sps[0], sm_s, sm_t, m[0]) <= dv[0]:
                    f.append(0)
                else:
                    f.append(1)
                if f[1] == 1:
                    y.append(s(I_sps[0], sm_s, m[1], m[0]) - dv[0])
                else:
                    y.append(s(I_sps[0], sm_s, sm_t, m[0]) + l(I_spl[0], m[0], m[1], m[0]) - dv[0])
            else:
                # Middle of stage. SFB is already ignited. We distinguish three cases:
                # 1. SFB has enough fuel for this whole step
                # 2. SFB already stopped past step, LFE is already burning
                # 3. SFB will stop burning this step, LFE will be ignited
                if f[i] == 0 or s(I_sps[i], m[i], sm_t, m[0]) <= dv[i]:
                    f.append(0)
                else:
                    f.append(1)
                if f[i+1] == 1:
                    y.append(s(I_sps[i], m[i], m[i+1], m[0]) - dv[i])
                elif f[i] == 0:
                    y.append(l(I_spl[i], m[i], m[i+1], m[0]) - dv[i])
                else:
                    y.append(s(I_sps[i], m[i], sm_t, m[0]) + l(I_spl[i], m[0], m[i+1], m[0]) - dv[i])
        # End (or start, if n == 0) of stage. We distinguish two cases:
        # 1. SFB already stopped past step, LFE is already burning or will be ignited
        # 2. SFB will stop burning this step, LFE will be ignited
        if f[n] == 0:
            y.append(l(I_spl[n], m[n], 0, m[0]) - dv[n])
        else:
            s_ig = sm_s if n == 0 else m[n]
            y.append(s(I_sps[n], s_ig, sm_t, m[0]) + l(I_spl[n], m[0], 0, m[0]) - dv[n])
        return y
    try:
        (sol, infodict, ier, mesg) = fsolve(equations, [0 for i in range(len(I_spl))], full_output=True)
    except ValueError:
        print("WARNING: Solution skipped due to ValueError")
        return None
    if not ier:
        return None
    return sol[0]

def engine_isp(eng, pressure):
    return [pressure[i]*eng.isp_atm + (1-pressure[i])*eng.isp_vac for i in range(len(pressure))]

def engine_force(eng, pressure):
    return pressure[0]*eng.F_vac*eng.isp_atm/eng.isp_vac + (1-pressure[0])*eng.F_vac

