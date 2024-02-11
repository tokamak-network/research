##Pure python Groth16 backend implementation
##It is porting code from https://codeocean.com/capsule/8850121/tree/v3

##Install 
# $pip install galois py_ecc

import galois
import random
from py_ecc.bn128 import(
    multiply, G1, G2, add, pairing, neg, curve_order
)

############################
###  1. PREPARING DATA   ###
############################

#Taking some time..
GF = galois.GF(curve_order)

pointInf1 = multiply(G1, curve_order) # None, point of infinity of G1
pointInf2 = multiply(G2, curve_order) # None, point of infinity of G2

Ap = [
    [-60.0, 110.0, -60.0, 10.0],
    [96.0, -136.0, 60.0, -8.0],
    [0.0, 0.0, 0.0, 0.0],
    [-72.0, 114.0, -48.0, 6.0],
    [48.0, -84.0, 42.0, -6.0],
    [-12.0, 22.0, -12.0, 2.0]
]

Bp = [
    [36.0, -62.0, 30.0, -4.0],
    [-24.0, 62.0, -30.0, 4.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0]
]

Cp = [
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [-144.0, 264.0, -144.0, 24.0],
    [576.0, -624.0, 216.0, -24.0],
    [-864.0, 1368.0, -576.0, 72.0],
    [576.0, -1008.0, 504.0, -72.0]
]

Z = [3456.0, -7200.0, 5040.0, -1440.0, 144.0]
R = [1, 3, 35, 9, 27, 30]

Ax = [ [int(num) % curve_order for num in vec] for vec in Ap ]
Bx = [ [int(num) % curve_order for num in vec] for vec in Bp ]
Cx = [ [int(num) % curve_order for num in vec] for vec in Cp ]
Zx = [ int(num) % curve_order for num in Z ]
Rx = [ int(num) % curve_order for num in R ]

#GF np array
npAx = GF(Ax)
npBx = GF(Bx)
npCx = GF(Cx)
npZx = GF(Zx)
npRx = GF(Rx)

#It is how multiply two matrix npAx.npRx
# npRax = npAx.transpose().dot(npRx)
# npRbx = npBx.transpose().dot(npRx)
# npRcx = npCx.transpose().dot(npRx)

#Same with above
npRax = npRx.dot(npAx)
npRbx = npRx.dot(npBx)
npRcx = npRx.dot(npCx)

#It is how transform list to polynomial
Rax = galois.Poly(npRax, order="asc")
Rbx = galois.Poly(npRbx, order="asc")
Rcx = galois.Poly(npRcx, order="asc")

Zx = galois.Poly(npZx, order="asc")
Rx = galois.Poly(npRx, order="asc")

Px = Rax * Rbx - Rcx

Hx = Px // Zx       #quotient
Remainder = Px % Zx #remainder

npHx = galois.Poly(Hx.coeffs, order="asc").coeffs

# Hx * Zx = R*Ax + R*Bx - R*Cx
print("Px % Zx  = 0 ?  {}".format(Remainder == 0))

############################
### 1. CRS CONSTRUCTION ###
############################

alpha = GF(3926)
beta = GF(3604)
gamma = GF(2971)
delta = GF(1357)
x_val = GF(3721)

tau = [alpha, beta, gamma, delta, x_val]

Ax_val = []
Bx_val = []
Cx_val = []

for i in range(len(Ax)):
    ax_single = galois.Poly(Ax[i], order="asc", field=GF)(x_val)
    Ax_val.append(ax_single)

for i in range(len(Bx)):
    bx_single = galois.Poly(Bx[i], order="asc", field=GF)(x_val)
    Bx_val.append(bx_single)

for i in range(len(Cx)):
    cx_single = galois.Poly(Cx[i], order="asc", field=GF)(x_val)
    Cx_val.append(cx_single)

Zx_val = Zx(x_val)
Hx_val = Hx(x_val)

numGates = len(Ax[0]) #length of Ax, n
numWires = len(Ax)    #height of Ax, m

#sigma1_1 = [G1 * alpha, G1 * beta, G1 * delta]
sigma1_1 = [multiply(G1, int(alpha)), multiply(G1, int(beta)), multiply(G1, int(delta))]
sigma1_2 = []
sigma1_3 = []
sigma1_4 = []
sigma1_5 = []

#sigma2_1 = [G2 * beta, G2 * gamma, G2 * delta]
sigma2_1 = [multiply(G2, int(beta)), multiply(G2, int(gamma)), multiply(G2, int(delta))]
sigma2_2 = []

#sigma1_2 = [G1*x^0, G1*x^1, G1*x^2, ... ,G1*x^(n-1)]
for i in range(numGates):
    val = x_val ** i
    sigma1_2.append(multiply(G1, int(val)))


#sigma1_3 = [
#     G1 * {beta*a_0(x) + alpha*b_0(x) + c_0(x)}/gamma,
#     G1 * {beta*a_1(x) + alpha*b_1(x) + c_1(x)}/gamma,
#     ...
#     G1 * {beta*a_l(x) + alpha*b_l(x) + c_l(x)}/gamma
# ]
# ## length(sigma1_3) == l
# ## l is num of public inputs ## 
VAL = [GF(0)]*numWires
for i in range(numWires):
    if i in [0, numWires-1]:
        val = (beta*Ax_val[i] + alpha*Bx_val[i] + Cx_val[i]) / gamma
        VAL[i] = val
        sigma1_3.append(multiply(G1, int(val)))
    else:
        sigma1_3.append((0, 0))

#sigma1_4 = [
#     G1 * {beta*a_{l+1}(x) + alpha*b_{l+1}(x) + c_{l+1}(x)}/delta,
#     G1 * {beta*a_{l+2}(x) + alpha*b_{l+2}(x) + c_{l+2}(x)}/delta,
#     ...
#     G1 * {beta*a_{m}(x)   + alpha*b_{m}(x)   + c_{m}(x)  }/delta
# ]
# ## length(sigma1_4) == (m - l)
for i in range(numWires):
    if i in [0, numWires-1]:
        sigma1_4.append((0, 0))
    else:
        val = (beta*Ax_val[i] + alpha*Bx_val[i] + Cx_val[i]) / delta
        sigma1_4.append(multiply(G1, int(val)))

#sigma1_5 = [
#     {x^0*Z(x)} / delta, 
#     {x^1*Z(x)} / delta, 
#     ... ,
#     {x^{n-2}*Z(x)} / delta
# ]
# ## length(sigma1_5) == (n - 1)
for i in range(numGates-1):
    sigma1_5.append(multiply(G1, int((x_val**i * Zx_val) / delta)))

#sigma2-2 = [G2*x^0, G2*x^1, G2*x^2, ... ,G2*x^(n-1)]
for i in range(numGates):
    sigma2_2.append(multiply(G2, int(x_val**i)))

lhs = Rax(x_val)*Rbx(x_val) - Rcx(x_val)
rhs = Zx_val*Hx_val

print("Is lhs == rhs ? : {}".format(lhs == rhs))

### 2. PROVING ###

r = GF(4106)
s = GF(4565)

#Build Proof_A, G1 based
proof_A = sigma1_1[0]
for i in range(numWires):
    temp = pointInf1
    for j in range(numGates):
        temp = add(temp, multiply(sigma1_2[j], int(Ax[i][j])))
    proof_A = add(proof_A, multiply(temp, int(npRx[i])))
proof_A = add(proof_A, multiply(sigma1_1[2], int(r)))

#Build proof_B, G2 based
proof_B = sigma2_1[0]
for i in range(numWires):
    temp = pointInf2
    for j in range(numGates):
        temp = add(temp, multiply(sigma2_2[j], int(Bx[i][j])))
    proof_B = add(proof_B, multiply(temp, int(npRx[i])))
proof_B = add(proof_B, multiply(sigma2_1[2], int(s)))

#Build temp_proof_B
temp_proof_B = sigma1_1[1]
for i in range(numWires):
    temp = pointInf1
    for j in range(numGates):
        temp = add(temp, multiply(sigma1_2[j], int(Bx[i][j])))
    temp_proof_B = add(temp_proof_B, multiply(temp, int(npRx[i])))
temp_proof_B = add(temp_proof_B, multiply(sigma1_1[2], int(s)))

#Build proof_C, G1 based
proof_C = add(add(multiply(proof_A, int(s)), multiply(temp_proof_B, int(r))), neg(multiply(sigma1_1[2], int(s*r))))

for i in range(1, numWires-1):
    proof_C = add(proof_C, multiply(sigma1_4[i], int(npRx[i])))

for i in range(numGates-1):
    proof_C = add(proof_C, multiply(sigma1_5[i], int(npHx[i])))

proof = [proof_A, proof_B, proof_C]

print("proofs : ", proof)
print("")

### 2.1 PROOF COMPLETENESS CHECK ###

A = alpha + Rax(x_val) + r*delta
B = beta + Rbx(x_val) + s*delta

C0 = GF(1) / delta
C1 = npRx[1:numWires-1]

C1_1 = GF([ax_val * beta for ax_val in Ax_val[1:numWires-1]])
C1_2 = GF([bx_val * alpha for bx_val in Bx_val[1:numWires-1]])
C1_3 = GF(Cx_val[1:numWires-1])

C2 = Hx_val*Zx_val
C3 = A*s + B*r - r*s*delta

C = C0 *((C1_1 + C1_2 + C1_3).dot(C1) + C2) + C3

lhs = A*B
# rhs = alpha*beta

rpub = GF([npRx[0], npRx[-1]]) 
valpub = GF([VAL[0], VAL[-1]]) 

rhs = alpha*beta + gamma*rpub.dot(valpub) + C*delta

print("#PROOF COMPLETENESS CHECK#")
print("rhs : {}".format(rhs))
print("lhs : {}".format(lhs))
print("rhs == lhs ? : {}".format(rhs == lhs))
print("proof A check : {}".format(proof_A == multiply(G1, int(A))))
print("proof B check : {}".format(proof_B == multiply(G2, int(B))))
print("proof C check : {}".format(proof_C == multiply(G1, int(C))))
print("")


##### 3. VERIFY ######

LHS = pairing(proof_B, proof_A)
RHS = pairing(sigma2_1[0], sigma1_1[0])

temp = None

for i in [0, numWires-1]:
  temp = add(temp, multiply(sigma1_3[i], int(npRx[i])))

RHS = (RHS * pairing(sigma2_1[1], temp)) * pairing(sigma2_1[2], proof_C)

print("LHS", LHS)
print("")
print("RHS", RHS)
print("")
print("Verification result (RHS == LHS)? : {}".format(RHS == LHS))