# https://risencrypto.github.io/Kate/
from py_ecc.fields import bn128_FQ as FQ
from py_ecc.bn128 import G1, G2, multiply, add, neg, pairing, curve_order

from functools import reduce
from random import randint

## IMPORTANT           ##
## MUST USE FR, not FQ ##
class FR(FQ):
    field_modulus = curve_order

# Multiply two polynomials
def multiply_polys(a, b):
    o = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            o[i + j] += a[i] * b[j]
    return o

# Evaluate a polynomial at a point
def eval_poly(poly, x):
    return sum([poly[i] * x**i for i in range(len(poly))])

# Divide a/b, return quotient and remainder
def div_polys(a, b):
    o = [0] * (len(a) - len(b) + 1)
    remainder = a
    while len(remainder) >= len(b):
        leading_fac = remainder[-1] / b[-1]
        pos = len(remainder) - len(b)
        o[pos] = leading_fac
        remainder = subtract_polys(remainder, multiply_polys(b, [0] * pos + [leading_fac]))[:-1]
    return o, remainder

# Add two polynomials
def add_polys(a, b, subtract=False):
    o = [0] * max(len(a), len(b))
    for i in range(len(a)):
        o[i] += a[i]
    for i in range(len(b)):
        o[i] += b[i] * (-1 if subtract else 1) # Reuse the function structure for subtraction
    return o

def subtract_polys(a, b):
    return add_polys(a, b, subtract=True)

#point_loc : lagrange index
#height : yi
#x_vec : x vector, list type
# l0 = (numerator / denumerator) * height
def mk_single_lagrange_term(point_loc, height, x_vec):
    denum = FR(1)
    # calculating denumerator of single lagrange term
    for i in range(len(x_vec)):
        if i != point_loc:
            denum *= x_vec[point_loc] - x_vec[i]
    o = [height / denum]
    #calculating numerator
    for i in range(len(x_vec)):
        if i != point_loc:
            # (x-x_0)(x-x_1) ... (x-x_(j-1))(x_x_(j+1))..(x-x_k) <- 라그랑주 분자 계산
            o = multiply_polys(o, [-x_vec[i], 1])
    return o

def lagrange_interpolation(x_vec, y_vec):
    assert len(x_vec) == len(y_vec)
    o = []
    for i in range(len(x_vec)):
        o = add_polys(o, mk_single_lagrange_term(i, y_vec[i], x_vec))
    return o

def commit(srs, poly):
    srsPolyList = [multiply(srs[i], int(poly[i])) for i in range(len(poly))]
    return reduce(add, srsPolyList)

# Making h(x) = SumOf_(i = 1 -> t){gamma^(i-1) * (fi(x)-fi(z)) / (x-z)}
# polys : list of polynomials
# t : number of polynomials in polys 
# z : pre-set z value for commitment
def mk_hx(polys, t, z):
    assert len(polys) == int(t) # t should be length of list polynomial
    Hx_list = []
    for i in range(1, int(t)+1):
        poly = polys[i-1] #fi(x)
        coeff = [gamma**(i-1)] #gamma^(i-1)
        numerator1 = subtract_polys(poly, [eval_poly(poly, z)]) #(fi(x)-fi(z))
        numerator2 = multiply_polys(coeff, numerator1) #gamma^(i-1) * (fi(x)-fi(z))
        denumerator = [-z, 1] #(x-z)
        o, remainder = div_polys(numerator2, denumerator) 
        assert sum(remainder) == 0 # remainder should be 0
        Hx_list.append(o)
    Hx = reduce(add_polys, Hx_list)
    return Hx
    

########################################################
## 5.SINGLE POINTS, MULTI POLY COMMIT & VERIFY SCHEME ##
########################################################

###############
## 5.0 Setup ##
###############

# In this example, assume that there are only 2 polynomial group(f_t,f_t') should be commited
# (It could be more like f_t'', f_t'''...)
# f1, f2, ... , ft in Fp[x] & t<d
# f1', f2', ... , ft' in Fp[x] & t'<d

d = 10 #degree of polynomial, d in Fp
t1 = 3 #number of polynomial to be commited for F1 group, t < d, t in Fp
t2 = 5 #number of polynomial to be commited for F2 group, t'< d, t' in Fp

z = FR(7) #preset value before commit, set by prover (or third party - need source), t < z, z in Fp

_a = FR(30) #toxic, it should be disappeared after created, no one knows forever.
SRSg1 = [multiply(G1, int(_a**i)) for i in range(d+1)] #Structured Reference String for G1
SRSg2 = [multiply(G2, int(_a**i)) for i in range(d+1)] #Structured Reference String for G2

################
## 5.1.Commit ##
################

print("Commiting...")

# random value from verifier to make combination of polynomial group. R = [1, r, r^2, r^3...]. 
# In this example, only [1, r] used(because only 2 polynomial group to be commited)
# r in Fp
r = FR(randint(0, curve_order-1))

# Polynomial Generation

# F1 Group
# F1_1(x) = f11_0*x^0 + f11_1*x^1 + f11_2*x^2 + ... + f11_d*x^d
# F1_2(x) = f12_0*x^0 + f12_1*x^1 + f12_2*x^2 + ... + f12_d*x^d
# ...
# F1_t(x) = f1t_0*x^0 + f1t_1*x^1 + f1t_2*x^2 + ... + f1t_d*x^d

# F2 Group
# F2_1(x) = f21_0*x^0 + f21_1*x^1 + f21_2*x^2 + ... + f21_d*x^d
# F2_2(x) = f22_0*x^0 + f22_1*x^1 + f22_2*x^2 + ... + f22_d*x^d
# ...
# F2_t(x) = f2t_0*x^0 + f2t_1*x^1 + f2t_2*x^2 + ... + f2t_d*x^d

Ftxs1 = []
Ftxs2 = []

for i in range(t1):
    ft1 = [FR(randint(0, curve_order-1)) for _ in range(d+1)]
    Ftxs1.append(ft1)

for i in range(t2):
    ft2 = [FR(randint(0, curve_order-1)) for _ in range(d+1)]
    Ftxs2.append(ft2)

#1) building opening_s1, s2
opening_s1 = [eval_poly(ft1, z) for ft1 in Ftxs1]
opening_s2 = [eval_poly(ft2, z) for ft2 in Ftxs2]

#2) building commitment of F(x)
Cf1i_g1 = [commit(SRSg1, f1i) for f1i in Ftxs1]
Cf2i_g1 = [commit(SRSg1, f2i) for f2i in Ftxs2]

#3) building commitment of H(x)

#random value from verifier to prover for C_h(or h(x)) construction
#gamma in Fp
gamma = FR(randint(0, curve_order-1)) 

#Commitment of h1(x), h2(x) using F1, F2 polynomial group
h1x = mk_hx(Ftxs1, t1, z)
h2x = mk_hx(Ftxs2, t2, z)
C_h1_g1 = commit(SRSg1, h1x)
C_h2_g1 = commit(SRSg1, h2x)

# then, C_h_g1 and opennings_s is given to verifier
print("## Commitment of f1(x),f2(x) created ")
print("## Commitment of h1(x),h2(x) created ")
print("## Openning s1, s2 created \n")

################
## 5.2.Verify ##
################

print("Verifying...")

#TODO : verifying explanation & implementation

# Verifier knows
# 1) C_h1_g1, C_h2_g1 = Commitment of h1(x), h2(x)                -> from prover
# 2) openning_s1, s2  = [s1, s2, ..., st1], [s1, s2, .., st2]     -> from prover
# 3) Cfi                                                          -> from prover
# 4) z, r -> given to prover from verifier before commit          -> from verifier