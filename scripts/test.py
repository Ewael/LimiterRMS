from math import log10, sqrt, pow

"""
    Dans un ampli,

        P = U ^ 2 / R
    <=> U = sqrt( P * R)

        U_out = U_in * 10 ^ ( gain_dB / 20 )
    <=> U_in = U_out / 10 ^ ( gain_dB / 20 )

    Or,

        dBu = 20 * log10( U / 0.775 )

    Donc, on a

        dBu_in = 20 * log10( U_out / 0.775 ) - gain_dB
"""

P_HP = 1600
P_amp = 4200
gain_amp = 41
impedance = 8

U_HP_max = sqrt(P_HP * impedance) # 113.14 V = tension max admissible par le HP
print(U_HP_max)

U_HP_max_amp_in = U_HP_max / pow(10, (gain_amp/20)) # 1 V = tension ampli IN qui donne U_HP_max en OUT
print(U_HP_max_amp_in)

dBu_max_in = 20 * log10(U_HP_max_amp_in / 0.775) # 2.28 dBu = max IN en dBu
print(dBu_max_in)