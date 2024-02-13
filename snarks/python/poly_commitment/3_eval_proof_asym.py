# https://risencrypto.github.io/Kate/
from py_ecc.fields import bn128_FQ as FQ
from py_ecc.bn128 import G1, G2, multiply, add, neg, pairing, curve_order

from functools import reduce

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

#######################################
##### 2.FULL OPEN & VERIFY SCHEME #####
#######################################

###############
## 2.0 SETUP ##
###############

_a = FR(30) #toxic, it should be disappear after created, no one knows.
SRSg1 = [multiply(G1, int(_a**i)) for i in range(d+1)]
SRSg2 = [multiply(G2, int(_a**i)) for i in range(d+1)]

################
## 2.1.Commit ##
################

b = FR(11) #value from verifier to prover

#This is polynomial should be committed.
#F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
#     = x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + 7*x^7 + 8*x^8 + 9*x^9 + 10*x^10
F = [FR(i) for i in range(d+1)]

#F(b) = c, prover has to provide a proof of it to verifier
c = eval_poly(F, b)

#Quotient Polynomial
#It should be polynomial because of Little Bezout's Theorem == no remainder
#Q(x) = (F(x) - F(b)) / (x - b)
# Qx = (F - c) / R([-b, 1])

numerator = subtract_polys(F, [c])
# print("numerator : ", numerator)
denumerator = [-b, 1]
# print("denumerator : ", denumerator)
Qx, remain = div_polys(numerator, denumerator)

# print("Qx : ", Qx)
# print("remainder : ", remain) # [0]

# Cq = Q(a)*G1
srsG1Qx = [multiply(SRSg1[i], int(Qx[i])) for i in range(len(Qx))]
Cq = reduce(add, srsG1Qx)

# Cf = F(a)*G1
srsG1Fx = [multiply(SRSg1[i], int(F[i])) for i in range(len(F))]
Cf = reduce(add, srsG1Fx)

# print("checking validity of Cq...")
# Cq_a = multiply(G1, int(eval_poly(Qx, _a)))
# print("Cq == Cq_a ? {}".format(Cq == Cq_a))

################
## 2.2.Verify ##
################

# Checking, e(Cq, a*G2-b*G2) == e(Cf - c*G1, G2) : ?

# why?
# Q(x) = (F(x) - c) / (x - b)
# (a - b) * Q(a) = (F(a) - c), evaluated at a
# (a - b) * Q(a) * G1 = (F(a) - c) * G1
# (a - b) * Cq = Cf - c * G1, because Q(a)*G1 = Cq, F(a)*G1 = Cf

# e((a - b)*Cq, G2) = e(Cf - c*G1, G2)
# e(Cq, (a-b)*G2) = e(Cf - c*G1, G2), because e(aA, B) = e(A, aB)
# so, e(Cq, (a*G2 - b*G2)) = e(Cf - c*G1, G2)

#building LHS
aG2 = multiply(G2, int(_a))      #a*G2
nbG2 = neg(multiply(G2, int(b))) #-b*G2
aG2nbG2 = add(aG2, nbG2)         #a*G2-b*G2
LHS = pairing(aG2nbG2, Cq)       #e(Cq, a*G2-b*G2)

# print("LHS : ", LHS)

#building RHS
ncG1 = neg(multiply(G1, int(c))) #-c*G1
cfncG1 = add(Cf, ncG1)           #Cf-c*G1
RHS = pairing(G2, cfncG1)        #e(Cf-c*G1, G2)

# print("RHS :",RHS)

print("LHS == RHS ? {}".format(LHS == RHS))