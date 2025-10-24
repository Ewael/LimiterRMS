from math import log10, sqrt, pow

"""
    Dans un ampli,

        P = U ^ 2 / R
    <=> U = sqrt( P * R )

        U_out = U_in * 10 ^ ( gain_dB / 20 )
    <=> U_in = U_out / 10 ^ ( gain_dB / 20 )

    Or,

        dBu = 20 * log10( U / 0.775 )

    Donc, on a

        dBu_in = 20 * log10( U_out / 0.775 ) - gain_dB
"""

P_HP = 1000
P_amp = 4200
gain_amp = 44
impedance = 8

 # tension max admissible par le HP
U_HP_max = sqrt(P_HP * impedance)
print(U_HP_max)

# tension ampli IN qui donne U_HP_max en OUT
U_HP_max_amp_in = U_HP_max / pow(10, (gain_amp/20))
print(U_HP_max_amp_in)

# max IN en dBu
dBu_max_in = 20 * log10(U_HP_max_amp_in / 0.775)
print(dBu_max_in)