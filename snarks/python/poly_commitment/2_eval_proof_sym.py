# https://risencrypto.github.io/Kate/
from py_ecc.fields import bn128_FQ as FQ
from py_ecc.bn128 import G1, multiply, add

from functools import reduce

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

_a = FQ(30) #toxic, it should be disappear after created, no one knows.
RS = [multiply(G1, int(_a**i)) for i in range(d+1)] #Reference String, {a^0*G,a^1*G, ... ,a^d*G}, length is d+1

#This is polynomial should be committed.
#F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
#     = x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + 7*x^7 + 8*x^8 + 9*x^9 + 10*x^10
F = [i for i in range(d+1)]

################
## 2.1.Commit ##
################

b = FQ(11) #value from verifier to prover

#This is polynomial should be committed.
#F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
#     = x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + 7*x^7 + 8*x^8 + 9*x^9 + 10*x^10
F = [FQ(i) for i in range(d+1)]

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

# Cq = Q(a)*G
rsQx = [multiply(RS[i], int(Qx[i])) for i in range(len(Qx))]
Cq = reduce(add, rsQx)

# Cf = F(a)*G
# Cf = sum([RS[i]*list(F)[i] for i in range(d+1)])
rsF = [multiply(RS[i], int(F[i])) for i in range(len(F))]
Cf = reduce(add, rsF)

print("checking validity of Cq...")
Cq_a = multiply(G1, int(eval_poly(Qx, _a)))
print("Cq == Cq_a ? {}".format(Cq == Cq_a))

################
## 2.2.Verify ##
################

# Checking, e(Cq, a*G-b*G) == e(Cf - c*G, G) : ?
# why?
# Q(x) = (F(x) - c) / (x - b)
# (a - b) * Q(a) = (F(a) - c), evaluated at a
# (a - b) * Q(a) * G = (F(a) - c) * G
# (a - b) * Cq = Cf - c * G, because Q(a)*G = Cq, F(a)*G = Cf
# e((a - b)*Cq, G) = e(Cf - c*G, G)
# e(Cq, (a-b)*G) = e(Cf - c*G, G), because e(aA, B) = e(A, aB)
# so, e(Cq, (a*G - b*G)) = e(Cf - c*G, G)

#######################################################
##### It is not working code                      #####
##### so this example is educational purpose only #####
#######################################################

# LHS = Cq.weil_pairing(RS[1] - b*g, EC.order())
# RHS = (Cf-c*g).weil_pairing(g, EC.order())
# print("LHS == RHS ? {}".format(LHS == RHS))