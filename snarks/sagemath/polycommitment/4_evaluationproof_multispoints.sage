# https://risencrypto.github.io/Kate/

import random
import math

p = 71 #Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.
q = p^2-1 #Field size for program, R1CS, and QAP. 

Z = IntegerModRing(q) #Z mod q
R.<x> = PowerSeriesRing(Z) #[a1, a2, a3 ...] = a0x^0 + a1x^2 + a2x^3 ...

FF = GF(p)
P.<x> = PowerSeriesRing(FF)

# Elliptic curve definition G1, G2
# % k=2;
# % % Elliptic curve: y^2=x^3+a*x+0
# % a=1;
# % b=0;
# % p=71; % Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.

EC = EllipticCurve(GF(71), [1,0])
g1 = EC.points()[12] #(11 : 8 : 1), order is 72, which is max among points

F.<z> = GF(71^2, modulus = x^2 + 1)
ECExt = EC.base_extend(F)
maxpoints = [p for p in ECExt.points() if p.order() == 72]
g2 = [mp for mp in maxpoints if mp[0] == 60][0] #extended generator

d = 10 #degree


#############################################################
##### 2.PARTIAL OPEN / EVALUATION PROOF & VERIFY SCHEME #####
#############################################################

###############
## 2.0 SETUP ##
###############

_a = Z(30) #toxic, it should be disappear after created, no one knows.
SRSg1 = [g1*(_a**i) for i in range(d+1)] #Reference String, {a^0*G1,a^1*G1, ... ,a^d*G1}, length is d+1
SRSg2 = [g2*(_a**i) for i in range(d+1)] #Reference String, {a^0*G2,a^1*G2, ... ,a^d*G2}, length is d+1


################
## 2.1.Commit ##
################

# #This is polynomial should be committed.
# #F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d

Fx = R([Z.random_element() for i in range(d+1)]).polynomial() ## FF based

# Another, it can be created from Lagrange Interpolation by 
# vector = [a1, a2, a3, ... , ai]
# points = [(1, a1),(2, a2), (3, a3), ... , (i, ai)]

t = d - 1 # t < d
# b = [FF.random_element() for _ in range(t)] # [b1, b2, ... , bt] which are given to prover from verifier
B = [Z.random_element() for _ in range(t)] # [b1, b2, ... , bt] which are given to prover from verifier
print("B : {}".format(B))

C = [Fx(b) for b in B]
print("C : {}".format(C))

px = [Z[x]((-B[i], 1)) for i in range(t)]
print("px : {}".format(px))
# Px = P(math.prod(px)).polynomial() # P(x) = (x-b1)(x-b2)...(x-bt)
Px = math.prod(px) # P(x) = (x-b1)(x-b2)...(x-bt)

(Qx, Rx) = Fx.quo_rem(Px) #Quotient and Remainder polynomial, F(x) = P(x)*Q(x) + R(x) 
# Qx = Fx / Px
# Rx = Fx % Px

# Qx = R(Qx)
# Rx = R(Rx)

print("F(x) : {}".format(Fx))
print("P(x) : {}".format(Px))
print("Q(x) : {}".format(Qx))
print("R(x) : {}".format(Rx))

# # Cq = Q(a)*G1
Cq1 = sum([ SRSg1[i]*Qx[i] for i in range(Qx.degree()+1)])
print("Cq1 : {}".format(Cq1))

#TODO : calculate Cf = F(a)*G1
Cf1 = sum([ SRSg1[i]*Fx[i] for i in range(Fx.degree()+1)])
print("Cf1 : {}".format(Cf1))

print("P(x)*Q(x)+R(x) == F(x) : {}".format(Px*Qx+Rx == Fx))

#Prover sends C, Cf, Cq to Verifier

################
## 2.2.Verify ##
################

# verifier knows
# P(x) -> Cp=P(a)*G -> how? (x-b1)(x-b2)…(x-bt)
# R(x) -> Cr=R(a)*G -> how? Lagrange Interpolation of zip(B,C)
# B, provided before commmitment
# Cf, Cq, C from prover

Px_verifier = math.prod(px)

Cp2 = sum([Px_verifier[i] * SRSg2[i] for i in range(Px.degree()+1)])
print("Cp2 : {}".format(Cp2))

#TODO : herer is the problem
# Rx_verifier = FF['x'].lagrange_polynomial(zip(B,C))
# Rx_verifier = R(Rx_verifier)

# Ri = PolynomialRing(QQ, 'x')
# Rr = PolynomialRing(Z, 'x')
# Rx_verifier = Ri.lagrange_polynomial(zip(B,C))

Rx_verifier = Rx

print("Rx from verifier : {}".format(Rx_verifier))
print("Rx from prover : {}".format(Rx))

Cr1 = sum([Rx_verifier[i] * SRSg1[i] for i in range(Rx.degree()+1)])
print("Cr1 : {}".format(Cr1))

# Verifier Checking

# 1. Checking F(b_i) == R(b_i)
Rbi = [Rx_verifier(b) for b in B]
print("( F(b_i) => C ) == R(b_i) ? : {}".format(C == Rbi))

# 2. Checking e(Cf1 - Cr1, G2) = e(Cq1, Cp2)

def weil(point1, point2):
    val = EC.isomorphism_to(ECExt)(point1).weil_pairing(point2, 72)
    return val

LHS = weil(Cf1 - Cr1, g2)
RHS = weil(Cq1, Cp2)
print("LHS : {}".format(LHS))
print("RHS : {}".format(RHS))
print("LHS == RHS ? : {}".format(LHS == RHS))

# Why?
# F(x) = P(x) * Q(x) + R(x)
# F(x) - R(x) = P(x) * Q(x)
# F(x) * G1 - R(x) * G1 = P(x) * Q(x) * G1, multiply both side G1
# F(a) * G1 - R(a) * G1 = P(a) * Q(a) * G1
# Cf1 - Cr1 = P(a) * Cq1

# e(Cf1 - Cr1, G2) = e(P(a) * Cq1, G2)
# e(Cf1 - Cr1, G2) = e(Cq1, P(a) * G2)
# e(Cf1 - Cr1, G2) = e(Cq1, Cp2)


#######################################

# Checking, e(Cq, a*G2-b*G2) == e(Cf - c*G1, G2) : ?

# why?
# Q(x) = (F(x) - c) / (x - b)
# (a - b) * Q(a) = (F(a) - c), evaluated at a
# (a - b) * Q(a) * G1 = (F(a) - c) * G1
# (a - b) * Cq = Cf - c * G1, because Q(a)*G1 = Cq, F(a)*G1 = Cf

# e((a - b)*Cq, G2) = e(Cf - c*G1, G2)
# e(Cq, (a-b)*G2) = e(Cf - c*G1, G2), because e(aA, B) = e(A, aB)
# so, e(Cq, (a*G2 - b*G2)) = e(Cf - c*G1, G2)

# def weil(point1, point2):
#     val = EC.isomorphism_to(ECExt)(point1).weil_pairing(point2, 72)
#     return val

# LHS = weil(Cq, SRSg2[1]-b*g2)
# RHS = weil(Cf-c*g1,  g2)

# print("LHS : {}".format(LHS))
# print("RHS : {}".format(RHS))
# print("LHS == RHS ? {}".format(LHS == RHS))

#### lagrange test ####


# points = [(FF.random_element(), FF.random_element()) for _ in range(10)]

# print(points)

# R = F['x']
# Px = R.lagrange_polynomial(points)
# P = R(Px)
# print(P)