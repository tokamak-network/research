# https://risencrypto.github.io/Kate/

p = 71 #Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.
q = p^2-1 #Field size for program, R1CS, and QAP. 

Z = IntegerModRing(q) #Z mod q
R.<x> = PowerSeriesRing(Z) #[a1, a2, a3 ...] = a0x^0 + a1x^2 + a2x^3 ...

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

#This is polynomial should be committed.
#F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
#     = x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + 7*x^7 + 8*x^8 + 9*x^9 + 10*x^10
# F = R([i for i in range(d+1)])


################
## 2.1.Commit ##
################

b = Z(11) #value from verifier to prover

#This is polynomial should be committed.
#F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
#     = x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + 7*x^7 + 8*x^8 + 9*x^9 + 10*x^10
F = R([i for i in range(d+1)])
# F = R([3,4,1,4,9,60,11,8,9,100,11])

#F(b) = c, prover has to provide a proof of it to verifier
c = F(b)

#Quotient Polynomial
#It should be polynomial because of Little Bezout's Theorem == no remainder
#Q(x) = (F(x) - F(b)) / (x - b)
Qx = (F - c) / R([-b, 1])

# Cq = Q(a)*G1
Cq = sum([ SRSg1[i]*list(Qx)[i] for i in range(Qx.degree())])

# Cf = F(a)*G1
Cf = sum([SRSg1[i]*list(F)[i] for i in range(d+1)])

# print("checking validity of Cq...")
# print("Cq (using RS) : {}".format(Cq)) -> (63 : 30 : 1)
# print("Cq (using toxic ) : {}".format(R(Qx.list())(_a) * g)) -> (63 : 30 : 1)

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

def weil(point1, point2):
    val = EC.isomorphism_to(ECExt)(point1).weil_pairing(point2, 72)
    return val

LHS = weil(Cq, SRSg2[1]-b*g2)
RHS = weil(Cf-c*g1,  g2)

print("LHS : {}".format(LHS))
print("RHS : {}".format(RHS))
print("LHS == RHS ? {}".format(LHS == RHS))