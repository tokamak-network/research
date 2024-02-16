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
def mk_hx(polys, t, z, gamma):
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
t1 = 4 #number of polynomial to be commited for F1 group, t < d, t in Fp
t2 = 5 #number of polynomial to be commited for F2 group, t'< d, t' in Fp

z1 = FR(7) #preset value before commit, set by prover (or third party - need source), t < z, z in Fp
z2 = FR(8)

_a = FR(30) #toxic, it should be disappeared after created, no one knows forever.
SRSg1 = [multiply(G1, int(_a**i)) for i in range(d+1)] #Structured Reference String for G1
SRSg2 = [multiply(G2, int(_a**i)) for i in range(d+1)] #Structured Reference String for G2

################
## 5.1.Commit ##
################

print("Commiting...")

# random value from verifier to make combination of polynomial group. R = [1, r, r^2, r^3...]. 
# In this example, only [1, r] used(because only 2 polynomial group to be combined and commited)
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
opening_s1 = [eval_poly(ft1, z1) for ft1 in Ftxs1]
opening_s2 = [eval_poly(ft2, z2) for ft2 in Ftxs2]

#2) building commitment of F(x)
Cf1i_g1 = [commit(SRSg1, f1i) for f1i in Ftxs1]
Cf2i_g1 = [commit(SRSg1, f2i) for f2i in Ftxs2]

#3) building commitment of H(x)

#random value from verifier to prover for C_h(or h(x)) construction
#gamma in Fp
gamma1 = FR(randint(0, curve_order-1))
gamma2 = FR(randint(0, curve_order-1)) 

#Commitment of h1(x), h2(x) using F1, F2 polynomial group
# h1(x) = SumOf_(i = 1->t1){gamma^(i-1)*(f1i(x)-si)/(x-z1)}
# h2(x) = SumOf_(i = 1->t2){gamma2^(i-1)*(f2i(x)-si)/(x-z2)}
# Ch1 = h1(a)*G1
# Ch2 = h2(a)*G1
h1x = mk_hx(Ftxs1, t1, z1, gamma1)
h2x = mk_hx(Ftxs2, t2, z2, gamma2)
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
# 2) openning s1 = [s1, s2, ..., st1], s2 = [s1, s2, .., st2]     -> from prover
# 3) Cf1i, Cf2i                                                   -> from prover
# 4) z1, z2, r -> given to prover from verifier before commit     -> from verifier

# 1) Checking all f1i(z) == s1i, f2i(z) == s2i ? for all opening s1= {s1, s2, .. , st1}, s2 = {s1, s2, ... , st2}
# 2) Checking e(C_h + r*C_h', a*G2) = e(H + z*C_h + z'*r*C_h', G2)
# where F  = SumOf_(i = 1->t ){gamma^(i-1)*f1i*G1}
#       v  = SumOf_(i = 1->t ){gamma^(i-1)*s1i*G1}
#       F' = SumOf_(i = 1->t ){gamma2^(i-1)*f2i*G1}
#       v' = SumOf_(i = 1->t ){gamma2^(i-1)*s2i*G1}
# and   H  = F + r*F' - v - r*v'

# why?
# Verifier has to check
# C_h  * (a - z ) = F  - v  ----- (1)
# C_h' * (a - z') = F' - v' ----- (2)
# combine (1),(2) with random r in Fp from Verifier
# C_h*(a-z) + r*C_h'*(a-z') = F + r*F' - v - r*v'
# Let H = F + r*F' - v - r*v'
# C_h*(a-z) + r*C_h'*(a-z') = H
# a*C_h + r*a*C_h' = H + z*C_h + z'*r*C_h'
# a(C_h + r*C_h') = H + z*C_h + z'*r*C_h'
# e(a(C_h + r*C_h'), G2) = e(H + z*C_h + z'*r*C_h', G2), using pairing
# e(C_h + r*C_h', a*G2) = e(H + z*C_h + z'*r*C_h', G2), using bilinearity


# 1) Checking all f1i(z1) == s1i, f2i(z2) == s2i ?
isTrueList1 = [eval_poly(Ftxs1[i], z1) == opening_s1[i] for i in range(t1)]
verify1result1 = reduce(lambda x, y: x*y, isTrueList1)

isTrueList2 = [eval_poly(Ftxs2[i], z2) == opening_s2[i] for i in range(t2)]
verify1result2 = reduce(lambda x, y: x*y, isTrueList2)

print("## 1.Checking all f1i(z1) == s1i, f2i(z2) == s2i ? {}".format(True == verify1result1 and True == verify1result2))

# 2) Checking e(C_h + r*C_h', a*G2) == e(H + z*C_h + z'*r*C_h', G2) ?
# where H = F + r*F' - v - r*v'

#LHS
LHS_g1 = add(C_h1_g1, multiply(C_h2_g1, int(r))) #C_h + r*C_h'
LHS_g2 = SRSg2[1] # a*G2
LHS_final = pairing(LHS_g2, LHS_g1) #e(C_h + r*C_h', a*G2)

#RHS
# F = SumOf_(i = 1->t ){gamma^(i-1)*Cfi }
# v = SumOf_(i = 1->t ){gamma^(i-1)*si*G1 }
def mk_F_minus_v(Cfi, gamma, t, opening_s, curve_gen):
    assert len(Cfi[0]) == len(curve_gen) #Cfi and curve_gen must in the same curve

    F_list = [multiply(Cfi[i-1], int(gamma**(i-1))) for i in range(1, t+1)] #{gamma^(i-1)*Cfi }
    F_g1 = reduce(add, F_list) # F = SumOf_(i = 1->t ){gamma^(i-1)*Cfi }
    
    siG1 = [multiply(curve_gen, int(si)) for si in opening_s] #si*G1
    v_list = [multiply(siG1[i-1], int(gamma**(i-1))) for i in range(1, t+1)] #{gamma^(i-1)*Cfi }
    v_g1 = reduce(add, v_list) # v = SumOf_(i = 1->t ){gamma^(i-1)*si*G1 }

    fmv = add(F_g1, neg(v_g1)) # F - v
    return fmv

# F - v & F' - v'
fmv1 = mk_F_minus_v(Cf1i_g1, gamma1, t1, opening_s1, G1) # F - v
fmv2 = mk_F_minus_v(Cf2i_g1, gamma2, t2, opening_s2, G1) # F' - v'
rfmv2 = multiply(fmv2, int(r)) # r*F' - r*v'
H = add(fmv1, rfmv2) # H = F - v + rF' - r*v'
z1ch1 = multiply(C_h1_g1, int(z1)) #z*C_h
z2rch2 = multiply(C_h2_g1, int(z2*r)) #z'*r*C_h'

RHS_g1 = add(add(H, z1ch1), z2rch2) # H + z*C_h + z'*r*C_h'

RHS_final = pairing(G2, RHS_g1) #e(H + z*C_h + z'*r*C_h', G2)

print("## 2.Checking e(C_h + r*C_h', a*G2) = e(H + z*C_h + z'*r*C_h', G2) ?")
print("LHS == RHS ? {}".format(LHS_final == RHS_final))
print("LHS : ")
print(LHS_final)
print("RHS : ")
print(RHS_final)

### Each Single polynomial test ####
# e(C_h1, a*G2−z1*G2) = e(F−v,G2)
# e(C_h2, a*G2−z2*G2) = e(F'−v',G2)

# print("")
# print("f1 side test : e(C_h1, a*G2−z1*G2) = e(F−v,G2) ?")

# f1_LHS = pairing(add(LHS_g2, neg(multiply(G2, int(z1)))), C_h1_g1) #e(C_h1, a*G2−z1*G2)
# f1_RHS = pairing(G2, fmv1) #e(F−v, G2)

# print("f1_LHS == f1_RHS ? {}\n".format(f1_LHS == f1_RHS))

# print("f2 side test : e(C_h2, a*G2−z2*G2) = e(F'−v',G2) ?")

# f2_LHS = pairing(add(LHS_g2, neg(multiply(G2, int(z2)))), C_h2_g1) #e(C_h1, a*G2−z1*G2)
# f2_RHS = pairing(G2, fmv2) #e(F'−v', G2)

# print("f2_LHS == f2_RHS ? {}".format(f2_LHS == f2_RHS))