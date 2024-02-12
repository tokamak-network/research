# https://risencrypto.github.io/Kate/
from py_ecc.fields import bn128_FQ as FQ
from py_ecc.bn128 import G1, multiply, add

d = 10 #degree

#######################################
##### 1.FULL OPEN & VERIFY SCHEME #####
#######################################

###############
## 1.0 SETUP ##
###############

_a = FQ(30) #toxic, it should be disappear after created, no one knows.
RS = [multiply(G1, int(_a**i)) for i in range(d+1)] #Reference String, {a^0*G,a^1*G, ... ,a^d*G}, length is d+1

# print("Reference string : ", RS)

#This is polynomial should be committed.
#F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
#     = x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + 7*x^7 + 8*x^8 + 9*x^9 + 10*x^10
F = [FQ(i) for i in range(d+1)]
print("target polynomial to be commited : ", F)

################
## 1.1.Commit ##
################

# prover knows F, but verifier doesn't know F
# prover doesn't know a, but knows RS
# prover sends Cf(commitment of F) to verifier

#This is polynomial should be committed.
#F(x) = f0*x^0 + f1*x + f2*x^2 + ... + fd*x^d
#     = x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + 7*x^7 + 8*x^8 + 9*x^9 + 10*x^10
F = [FQ(i) for i in range(d+1)]

# This is a commitment from prover
# Cf = F(a)*G
#    = (f0 + f1*a + f2*a^2 + ... + fd*a^d)*G
#    = f0*a^0*G + f1*a^1*G + f2*a^2*G + ... + fd*a^d*G

Cf = None #point of infinite

for i in range(d+1):
    Cfi = multiply(RS[i], int(F[i]))
    Cf =  add(Cf, Cfi)

print("Prover's commitment(Cf) : {}".format(Cf))

# print("checking validity of Cf...")
# print("Cf (using RS) : {}".format(Cf)) -> (6 : 68 : 1)
# print("Cf (using toxic ) : {}".format(F(a)*g)) -> (6 : 68 : 1)

################
## 1.2.Verify ##
################

# Prover opens(sends) full F to verifier
# Verifier using F, Cf to check if the commitment is valid or not

vCf = None #point of infinite

for i in range(d+1):
    vCfi = multiply(RS[i], int(F[i]))
    vCf = add(vCf, vCfi)

print("Cf == vCf ? {}".format(Cf == vCf))
# print("Cf : {}".format(Cf))
# print("vCf : {}".format(vCf))