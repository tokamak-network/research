##Pure python Groth16 backend implementation
##It is porting code from https://codeocean.com/capsule/8850121/tree/v3

##INSTALL 
# $pip install galois py_ecc

##RUN
# python groth16FR.py

from py_ecc.fields import bn128_FQ as FQ
from py_ecc import bn128

from random import randint

g1 = bn128.G1
g2 = bn128.G2

# FR = FQ
# FR.field_modulus = bn128.curve_order

class FR(FQ):
    field_modulus = bn128.curve_order

#TEST pairing
mult = bn128.multiply
pairing = bn128.pairing
add = bn128.add
neg = bn128.neg

pointInf1 = mult(g1, bn128.curve_order) # None
pointInf2 = mult(g2, bn128.curve_order) # None


# a = pairing(mult(g2,10),g1)
# b = pairing(g2, mult(g1,10))
# print(a == b)

# Multiply two polynomials
def multiply_polys(a, b):
    o = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            o[i + j] += a[i] * b[j]
    return o

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

# Evaluate a polynomial at a point
def eval_poly(poly, x):
    return sum([poly[i] * x**i for i in range(len(poly))])

# Mod q of all matrix elements
def to_matrix_mod(matrix, q):
    target = []
    for row in matrix:
        temp_row = []
        for val in row:
            temp_row.append(int(val) % q)
        target.append(temp_row)
    return target

#TARGET POLYNOMIAL

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


Ax = [ [FR(int(num)) for num in vec] for vec in Ap ]
Bx = [ [FR(int(num)) for num in vec] for vec in Bp ]
Cx = [ [FR(int(num)) for num in vec] for vec in Cp ]
Zx = [ FR(int(num)) for num in Z ]
Rx = [ FR(int(num)) for num in R ]

# Rax = [multiply_polys(Rx, vec)for vec in Ax]
# Rbx = [multiply_polys(Rx, vec)for vec in Bx]
# Rcx = [multiply_polys(Rx, vec)for vec in Cx]

def multiply_vec_matrix(vec, matrix):
    # len(vec) == len(matrix.row)
    assert not len(vec) == len(matrix[0])
    target = [FR(0)]*len(vec)
    for i in range(len(matrix)): #loop num of rows == size of vec, 0-5
        for j in range(len(matrix[0])): #loop num of columns, 0-3
            target[j] = target[j] + vec[i] * matrix[i][j]
    return target

    
Rax = multiply_vec_matrix(R, Ax)
Rbx = multiply_vec_matrix(R, Bx)
Rcx = multiply_vec_matrix(R, Cx)

#Px = Rax * Rbx - Rcx
Px = subtract_polys(multiply_polys(Rax, Rbx), Rcx)

q, r = div_polys(Px, Zx)

Hx = q

# r should be zero

#q = [14592161914559516814830937163504850059130874104865215775126025263096817472385,
#  20672229378959315487677160981631870917102071648559055681428535789387158085901,
#  9728107943039677876553958109003233372753916069910143850084016842064544981589,
#  0,
#  0,
#  0,
#  0]

#r = [0, 0, 0, 0]

alpha = FR(3926)
beta = FR(3604)
gamma = FR(2971)
delta = FR(1357)
x_val = FR(3721)

# alpha = FR(randint(0, bn128.curve_order))
# beta = FR(randint(0, bn128.curve_order))
# gamma = FR(randint(0, bn128.curve_order))
# delta = FR(randint(0, bn128.curve_order))
# x_val = FR(randint(0, bn128.curve_order))

tau = [alpha, beta, gamma, delta, x_val]

Ax_val = []
Bx_val = []
Cx_val = []

for i in range(len(Ax)):
    ax_single = eval_poly(Ax[i], x_val)
    Ax_val.append(ax_single)

for i in range(len(Bx)):
    bx_single = eval_poly(Bx[i], x_val)
    Bx_val.append(bx_single)

for i in range(len(Cx)):
    cx_single = eval_poly(Cx[i], x_val)
    Cx_val.append(cx_single)

Zx_val = eval_poly(Zx, x_val)
Hx_val = eval_poly(Hx, x_val)

#numGates = len(Ax.columns())
#numWires = len(Ax.rows())

numGates = len(Ax[0])
numWires = len(Ax)

sigma1_1 = [mult(g1, int(alpha)), mult(g1, int(beta)), mult(g1, int(delta))]

sigma1_2 = []
sigma1_3 = []
sigma1_4 = []
sigma1_5 = []

sigma2_1 = [mult(g2, int(beta)), mult(g2, int(gamma)), mult(g2, int(delta))]
sigma2_2 = []

#sigma1_2
for i in range(numGates):
    val = x_val ** i
    sigma1_2.append(mult(g1, int(val)))

#sigma1_3
VAL = [FR(0)]*numWires
for i in range(numWires):
    if i in [0, numWires-1]:
        val = (beta*Ax_val[i] + alpha*Bx_val[i] + Cx_val[i]) / gamma
        VAL[i] = val
        sigma1_3.append(mult(g1, int(val)))
    else:
        sigma1_3.append((FQ(0), FQ(0)))

#sigma1_4
for i in range(numWires):
    if i in [0, numWires-1]:
        sigma1_4.append((FQ(0), FQ(0)))
    else:
        val = (beta*Ax_val[i] + alpha*Bx_val[i] + Cx_val[i]) / delta
        sigma1_4.append(mult(g1, int(val)))

#sigma1_5
for i in range(numGates-1):
    sigma1_5.append(mult(g1, int((x_val**i * Zx_val) / delta)))

#sigma2-2
for i in range(numGates):
    # sigma2_2.append(h*(Z(x_val^i)))
    sigma2_2.append(mult(g2, int(x_val**i)))

##CRS validity check

# Ax_val = vector(Z, Ax_val)
# Bx_val = vector(Z, Bx_val)
# Cx_val = vector(Z, Cx_val)

# Zx_val = Z(Zx_val)
# Hx_val = Z(Hx_val)
    
def multiply_vec_vec(vec1, vec2):
    assert len(vec1) == len(vec2)
    target = 0
    size = len(vec1)
    for i in range(size):
        target += vec1[i]*vec2[i]
    return target

lhs = multiply_vec_vec(Rx, Ax_val) * multiply_vec_vec(Rx, Bx_val) - multiply_vec_vec(Rx, Cx_val)
rhs = Zx_val * Hx_val

# lhs = Z((Rx*Ax_val)*(Rx*Bx_val)-(Rx*Cx_val))
# rhs = Zx_val*Hx_val

print("polynomial verification")
print(lhs == rhs)


### 2. PROVING ###

r = FR(4106)
s = FR(4565)

# r = FR(randint(0, bn128.curve_order))
# s = FR(randint(0, bn128.curve_order))

#Build Proof_A, g1 based
proof_A = sigma1_1[0]
for i in range(numWires):
    temp = pointInf1
    for j in range(numGates):
        temp = add(temp, mult(sigma1_2[j], int(Ax[i][j])))
    proof_A = add(proof_A, mult(temp, int(Rx[i])))
proof_A = add(proof_A, mult(sigma1_1[2], int(r)))


#Build proof_B, g2 based
proof_B = sigma2_1[0]
for i in range(numWires):
    temp = pointInf2
    for j in range(numGates):
        temp = add(temp, mult(sigma2_2[j], int(Bx[i][j])))
    proof_B = add(proof_B, mult(temp, int(Rx[i])))
proof_B = add(proof_B, mult(sigma2_1[2], int(s)))


#Build temp_proof_B
temp_proof_B = sigma1_1[1]
for i in range(numWires):
    temp = pointInf1
    for j in range(numGates):
        temp = add(temp, mult(sigma1_2[j], int(Bx[i][j])))
    temp_proof_B = add(temp_proof_B, mult(temp, int(Rx[i])))
temp_proof_B = add(temp_proof_B, mult(sigma1_1[2], int(s)))

#Build proof_C, g1_based
# proof_C = add(add(mult(proof_A, int(s)), mult(temp_proof_B, int(r))), neg(mult(sigma1_1[2], int(r*s))))
proof_C = add(add(mult(proof_A, int(s)), mult(temp_proof_B, int(r))), neg(mult(mult(sigma1_1[2], int(s)), int(r))))

for i in range(1, numWires-1):
    proof_C = add(proof_C, mult(sigma1_4[i], int(Rx[i])))

for i in range(numGates-1):
    proof_C = add(proof_C, mult(sigma1_5[i], int(Hx[i])))


proof = [proof_A, proof_B, proof_C]

print("proofs : ", proof)
print("")

### 2.1 PROOF COMPLETENESS CHECK ###

def scalar_vec(scalar, vec):
    return [scalar*num for num in vec]

A = alpha + multiply_vec_vec(Rx, Ax_val) + r*delta
B = beta + multiply_vec_vec(Rx, Bx_val) + s*delta

# C1 = scalar_vec(1/delta, Rx[1:numWires-1])
# C2_1 = scalar_vec(beta, Ax_val[1:numWires-1])
# C2_2 = scalar_vec(alpha, Bx_val[1:numWires-1])
# C2_3 = Cx_val[1:numWires-1]
# C3 = Hx_val*Zx_val
# C4 = A*s + B*r - r*s*delta

# C = multiply_vec_vec(C1, (add_polys(add_polys(C2_1, C2_2), C2_3))) + C3 + C4


# C0 * {C1*(C1_1+C1_2+C1_3) + C2} + C3
C0 = 1/delta 
C1 = Rx[1:numWires-1] #vec
C1_1 = scalar_vec(beta, Ax_val[1:numWires-1])
C1_2 = scalar_vec(alpha, Bx_val[1:numWires-1])
C1_3 = Cx_val[1:numWires-1]
C2 = Hx_val*Zx_val
C3 = A*s + B*r - r*s*delta

C1112 = add_polys(C1_1, C1_2) # vec
C111213 = add_polys(C1112, C1_3) # vec
C1111213 = multiply_vec_vec(C1, C111213) #num

C = C0 * (C1111213 + C2) + C3

# C = multiply_vec_vec(C1, (add_polys(add_polys(C2_1, C2_2), C2_3))) + C3 + C4

lhs = A*B #21888242871839275222246405745257275088548364400416033032405666501928354297837

rhs = alpha*beta #14149304

rpub = [Rx[0], Rx[-1]] #[1, 30]
valpub = [VAL[0], VAL[-1]] 
#[17858330771234736835653075572704017103548042849750409710240473560856989375368,
# 3057428741774924004453806255227791707084339019243572619533744442206670609805]

rhs = rhs + gamma*multiply_vec_vec(rpub,valpub) #12058091336480024
rhs = rhs + C*delta #21888242871839275222246405745257275088548364400414254943408259015785828911597

print("#PROOF COMPLETENESS CHECK#")
print("rhs : {}".format(rhs))
print("lhs : {}".format(lhs))
print("rhs == lhs ? : {}".format(rhs == lhs))
print("proof A check : {}".format(proof_A == mult(g1, int(A))))
print("proof B check : {}".format(proof_B == mult(g2, int(B))))
print("proof C check : {}".format(proof_C == mult(g1, int(C))))
print("")

# A = alpha + Rx*Ax_val + r*delta
# B = beta + Rx*Bx_val + s*delta
# C = 1/delta*Rx[1:numWires-1]*(beta*Ax_val[1:numWires-1] + alpha*Bx_val[1:numWires-1] + Cx_val[1:numWires-1]) + Hx_val*Zx_val + A*s + B*r + (-r*s*delta)

# lhs = A*B

# rhs = alpha*beta #2024

# rpub = [Rx[0], Rx[-1]]
# valpub = [VAL[0], VAL[-1]]

# rhs = rhs + gamma*vector(rpub)*vector(valpub)  #4040
# rhs = rhs + C*delta #984

# result = (proof_A == g*A) and (proof_B == B*h) and (proof_C == C*g)

# print("proof completeness check : {}".format(result and lhs==rhs))

##### 3. VERIFY ######
    
LHS = pairing(proof_B, proof_A)
RHS = pairing(sigma2_1[0], sigma1_1[0])

temp = None

for i in [0, numWires-1]:
  temp = add(temp, mult(sigma1_3[i], int(Rx[i])))

RHS = (RHS * pairing(sigma2_1[1], temp)) * pairing(sigma2_1[2], proof_C)

print("LHS", LHS)
print("")
print("RHS", RHS)
print("")
print("Verification result (RHS == LHS)? : {}".format(RHS == LHS))