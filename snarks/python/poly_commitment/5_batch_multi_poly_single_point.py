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
    

########################################################
## 5.SINGLE POINTS, MULTI POLY COMMIT & VERIFY SCHEME ##
########################################################

###############
## 5.0 Setup ##
###############

d = 10 #degree of polynomial, d in Fp
t = 3 #number of polynomial to be commited, t < d, t in Fp
z = FR(7) #preset value before commit, set by prover (or third party - need source), t < z, z in Fp

_a = FR(30) #toxic, it should be disappeared after created, no one knows forever.
SRSg1 = [multiply(G1, int(_a**i)) for i in range(d+1)] #Structured Reference String for G1
SRSg2 = [multiply(G2, int(_a**i)) for i in range(d+1)] #Structured Reference String for G2

################
## 5.1.Commit ##
################

print("Commiting...")

# #This is polynomial would be committed
# #F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d

# Polynomial Generation
# F1(x) = f1_0*x^0 + f1_1*x^1 + f1_2*x^2 + ... + f1_d*x^d
# F2(x) = f2_0*x^0 + f2_1*x^1 + f2_2*x^2 + ... + f2_d*x^d
# ...
# Ft(x) = ft_0*x^0 + ft_1*x^1 + ft_2*x^2 + ... + ft_d*x^d
Ftxs = []
for i in range(t):
    ft = [ FR(randint(0, curve_order-1)) for _ in range(d+1) ]
    Ftxs.append(ft)

openings_s = [ eval_poly(ft, z) for ft in Ftxs ]

gamma = FR(randint(0, curve_order-1)) #random value from verifier to prover


# Hx = SumOf_(i = 1 -> t){gamma^(i-1) * (fi(x)-fi(z)) / (x-z)}
Hx_list = []
for i in range(1, t+1):
    poly = Ftxs[i-1] #fi(x)
    coeff = [gamma**(i-1)] #gamma^(i-1)
    numerator1 = subtract_polys(poly, [eval_poly(poly, z)]) #(fi(x)-fi(z))
    numerator2 = multiply_polys(coeff, numerator1) #gamma^(i-1) * (fi(x)-fi(z))
    denumerator = [-z, 1] #(x-z)
    o, remainder = div_polys(numerator2, denumerator) # remainder should be [0]
    Hx_list.append(o)

Hx = reduce(add_polys, Hx_list)

#Commitemnt of Hx, Ch(g1 based)
C_h_g1 = commit(SRSg1, Hx)

# then, C_h_g1 and opennings_s is given to verifier
print("## Commitment of h(x) : {}".format(C_h_g1))
print("## Openning S : {}".format(openings_s))

################
## 5.2.Verify ##
################

print("Verifying...")

# Verifier knows
# 1) C_h_g1 = Commitment of Hx      -> from prover
# 2) openning_s = [s1, s2, ..., st] -> from prover
# 3) Cfi                            -> from prover
# 4) SRSg1, SRSg2                   -> from setup phase

# 1) Checking all fi(z) == si ? for all openings_s = {s1, s2, .. , si}
# 2) Checking e(Ch_g1, a*G2-z*G2) == e(F-v, G2 ) 
# where F = SumOf_(i = 1->t ){gamma^(i-1)*Cfi }
#       v = SumOf_(i = 1->t ){gamma^(i-1)*si*G1 }

# why? 
# Verifer has to check if
# h(x) = SumOf_(i = 1->t){gamma^(i-1)*(fi(x)-si)/(x-z)}
# h(x)*(x-z) = SumOf_(i = 1->t){gamma^(i-1)*(fi(x)-si)}
# h(x)*(x-z) = SumOf_(i = 1->t){gamma^(i-1)*(fi(x))} -  SumOf_(i = 1->t){gamma^(i-1)*si}
# h(x)*(x-z) = SumOf_(i = 1->t){gamma^(i-1)*(fi(x))} -  SumOf_(i = 1->t){gamma^(i-1)*si}
# multiplying both side G1, evaluate at a
# h(a)*G1*(a-z) = SumOf_(i = 1->t){gamma^(i-1)*fi(a)*G1} -  SumOf_(i = 1->t){gamma^(i-1)*si*G1}
# Ch_g1 = h(a)*G1
# Cfi_g1 = fi(a)*G1
# Ch_g1*(a-z) = SumOf_(i = 1->t){gamma^(i-1)*Cfi_g1} -  SumOf_(i = 1->t){gamma^(i-1)*si*G1} ----- equation 1
# Let F = SumOf_(i = 1->t){gamma^(i-1)*Cfi_g1}
# Let v = SumOf_(i = 1->t){gamma^(i-1)*si*G1}
# using F, v substituting equation 1, then
# Ch_g1*(a-z) = F - v           ------ equation 2
# using pairing, bilinearity property
# e(Ch_g1*(a-z), G2) = e(F - v, G2)
# e(Ch_g1, a*G2 - z*G2) = e(F - v, G2)

# 1) Checking all fi(z) == si ? for all openings_s = {s1, s2, .. , si}
isTrueList = [ eval_poly(Ftxs[i], z) == openings_s[i] for i in range(t)]
verify1result = reduce(lambda x, y: x*y, isTrueList)

print("## 1.Checking all R(bi) == ci ? {}".format(True == verify1result))

#TODO : checking this
# 2) Checking e(Ch_g1, a*G2-z*G2) == e(F-v, G2) 
# where F = SumOf_(i = 1->t ){gamma^(i-1)*Cfi }
#       v = SumOf_(i = 1->t ){gamma^(i-1)*si*G1 }

# LHS building
aG2zG2 = add(multiply(G2, int(_a)), neg(multiply(G2, int(z))))
LHS = pairing(aG2zG2, C_h_g1)

#RHS building
Cfi_g1 = [commit(SRSg1, fi) for fi in Ftxs] #Cfi
F_list = [multiply(Cfi_g1[i-1], int(gamma**(i-1)))  for i in range(1, t+1)] #{gamma^(i-1)*Cfi }
F_g1 = reduce(add, F_list) # F = SumOf_(i = 1->t ){gamma^(i-1)*Cfi }

siG1 = [multiply(G1, int(si)) for si in openings_s] #si*G1
v_list = [multiply(siG1[i-1], int(gamma**(i-1)))  for i in range(1, t+1)] #{gamma^(i-1)*Cfi }
v_g1 = reduce(add, v_list) # v = SumOf_(i = 1->t ){gamma^(i-1)*si*G1 }

fmv = add(F_g1, neg(v_g1)) # F - v
RHS = pairing(G2, fmv) # e(F-v, G2)

print("## 2.Checking e(Ch_g1, a*G2-z*G2) == e(F-v, G2) ?")
print("LHS == RHS ? {}".format(LHS == RHS))