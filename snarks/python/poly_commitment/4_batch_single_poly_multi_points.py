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

d = 10 #degree

########################################################
## 4.MULTI POINTS, SINGLE POLY COMMIT & VERIFY SCHEME ##
########################################################

###############
## 4.0 Setup ##
###############

_a = FR(30) #toxic, it should be disappeared after created, no one knows forever.
SRSg1 = [multiply(G1, int(_a**i)) for i in range(d+1)]
SRSg2 = [multiply(G2, int(_a**i)) for i in range(d+1)]

################
## 4.1.Commit ##
################

print("Commiting...")

# #This is polynomial would be committed
# #F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
Fx = [FR(i) for i in range(d+1)]

t = d - 1 # t < d, number of values from verifier to prover

# B = {b1, b2, b3, .. , bt}, values from verifier to prover before commit
B = [FR(randint(0, FR.field_modulus-1)) for _ in range(t)]
# B = [FR(b+1) for b in range(t)]
print("B : {}".format(B))

# C = {F(b1), F(b2), ... , F(bt)} = {c1, c2, .. , ct}
# it will be given to verifier after commitment computation
C = [eval_poly(Fx, b) for b in B]
print("C : {}".format(C))

# P(x) = (x-b1)(x-b2)..(x-bt)
PxBeforeDist = [[-b, 1] for b in B] 
Px = reduce(multiply_polys, PxBeforeDist)

## Checking Px ##
pxTermCheckList = [0 == eval_poly(Px, b) for b in B]
isPxValid = reduce(lambda a, b : a*b, pxTermCheckList)
print("checking validity of P(x).. {}".format(isPxValid == True))
# for b in B:
#     print(0 == eval_poly(Px, b))

#F(x) = P(x)Q(x) + R(x), F(x) always dividable by P(x) because t>d
Qx, Rx = div_polys(Fx, Px)

#checking F(x) = P(x)Q(x) + R(x)
lhs = Fx
rhs = add_polys(multiply_polys(Px, Qx), Rx)
print("checking F(x) = P(x)Q(x) + R(x) ? {}".format(lhs == rhs))

# {Cq, C} are given to Verifier
# Cq = Q(a)*G1 , C = {c1, c2, .., ct}, Cf = F(a)*G1

# Cq1 = Q(a)*G1
srsG1Qx = [multiply(SRSg1[i], int(Qx[i])) for i in range(len(Qx))]
Cq1 = reduce(add, srsG1Qx)

# Cf1 = F(a)*G1
srsG1Fx = [multiply(SRSg1[i], int(Fx[i])) for i in range(len(Fx))] #lenth = d+1
Cf1 = reduce(add, srsG1Fx)

# checking validity of Cq1, Cf1
Cq1_a = multiply(G1, int(eval_poly(Qx, _a)))
print("checking validity of Cq1... {}".format(Cq1 == Cq1_a))

Cf1_a = multiply(G1, int(eval_poly(Fx, _a)))
print("checking validity of Cf1... {}".format(Cf1 == Cf1_a))
print("")
# print("Cf1 == Cf1_a ? {}".format(Cf1 == Cf1_a))

################
## 4.2.Verify ##
################

print("Verifying...")

# Verifier knows
# B = {b1, b2, ... , bt}, t<d -> it is preset values before committing
# C = {c1, c2, ... , ct}, t<d -> from Prover
# Cq1 = Q(a)*G1               -> from Prover
# Cf1 = F(a)*G1               -> from Prover
# R(x) / Cr1 = R(a)*G1        -> from Prover or lagrnage interpolation using B,C
# P(x) / Cp2 = P(a)*G2        -> because Prover can build. P(x) = (x-b1)(x-b2)...(x-bi)

# 1) Checking F(bi) == R(bi) ? for all B = {b1, b2, .. , bi} 
# Check all R(bi) == ci
# using R(x) means using lagnrage interpolation with B,C

# 2) Checking e(Cf1 - Cr1, G2) == e(Cq1, Cp2)

# why?
# F(x) =? P(x)Q(x) + R(x)
# F(x) - R(x) =? P(x)Q(x)
# F(x)*G1 - R(x)*G1 =? P(x)*Q(x)*G1, multiply both side by G1
# F(a)*G1 - R(a)*G1 =? P(a)*Q(a)*G1, evaluate at a
# Cf1 - Cr1 =? P(a)*Cq1
# e(Cf1 - Cr1, G2) =? e(P(a)*Cq1, G2), applying pairing map both sides
# e(Cf1 - Cr1, G2) =? e(Cq1, P(a)*G2), bilinearity
# so, e(Cf1 - Cr1, G2) =? e(Cq1, Cp2)

# TODO : lagnrage interpolation using B,C to make R(x)
# 1) checking for all R(bi) == ci
isTrueList = [eval_poly(Rx, B[i]) == C[i] for i in range(t)]
verify1result = reduce(lambda x, y: x*y, isTrueList)

print("## 1 Checking all R(bi) == ci ? {}".format(True == verify1result))

# 2) Checking e(Cf1 - Cr1, G2) == e(Cq1, Cp2)

#Cr1 = R(a)*G1
srsG1Rx = [multiply(SRSg1[i], int(Rx[i])) for i in range(len(Rx))]
Cr1 = reduce(add, srsG1Rx)

#Cp2 = P(a)*G2
srsG2Px = [multiply(SRSg2[i], int(Px[i])) for i in range(len(Px))]
Cp2 = reduce(add, srsG2Px)

#checking Cr1
Cr1_a = multiply(G1, int(eval_poly(Rx, _a)))
print("checking validity of Cr1... {}".format(Cr1 == Cr1_a))
# print("Cr1 == Cr1_a ? {}".format(Cr1 == Cr1_a))

#checking Cp2
Cp2_a = multiply(G2, int(eval_poly(Px, _a)))
print("checking validity of Cp2... {}".format(Cp2 == Cp2_a))
# print("Cp2 == Cp2_a ? {}".format(Cp2 == Cp2_a))

LHS = pairing(G2, add(Cf1, neg(Cr1)))
RHS = pairing(Cp2, Cq1)

print("## 2 Checking e(Cf1 - Cr1, G2) == e(Cq1, Cp2) ? ")
print("LHS == RHS ? {}".format(LHS == RHS))