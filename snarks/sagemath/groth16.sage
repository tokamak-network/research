#  Ap:
#           480        3944         660        4888          12
#            24        5016        5030          12        5038
#          4944         200        4900          40        5036
#            24        4990          35        5030           1
#            24        4990          35        5030           1
#             0           0           0           0           0

# % Bp:
# %           24        4990          35        5030           1
# %            0          90        4947          30        5037
# %            0        5000          58        5020           2
# %            0           0           0           0           0
# %            0           0           0           0           0
# %            0           0           0           0           0

# % Cp:
# %            0           0           0           0           0
# %         3600        4704        3264        1344        4944
# %         2880        4272        2496          48         384
# %          720        3888        2016        3312         144
# %         2160         816        1104        1056        4944
# %          576        3840         840        4800          24

# % Zp:
# %         4920         274        4815          85        5025           1

# % R:
# %            1           2           4           8           4        5028

#To run : load("hello.sage") in sage command line program

### DATA 1 ###

# Ap = [
#     [480, 3944, 660, 4888, 12],
#     [24, 5016, 5030, 12, 5038],
#     [4944, 200, 4900, 40, 5036],
#     [24, 4990, 35, 5030, 1],
#     [24, 4990, 35, 5030, 1],
#     [0, 0, 0, 0, 0]
#     ]

# Bp = [
#     [24, 4990, 35, 5030, 1],
#     [0, 90, 4947, 30, 5037],
#     [0, 5000, 58, 5020, 2],
#     [0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0]
#     ]

# Cp = [
#     [0, 0, 0, 0, 0],
#     [3600, 4704, 3264, 1344, 4944],
#     [2880, 4272, 2496, 48, 384],
#     [720, 3888, 2016, 3312, 144],
#     [2160, 816, 1104, 1056, 4944],
#     [576, 3840, 840, 4800, 24]
#     ]

# Zp = [4920, 274, 4815, 85, 5025, 1]

# R = [1, 2, 4, 8, 4, 5028]

### DATA2 ###

Ap = [
    [4980, 110, 4980, 10],
    [96, 4904, 60, 5032],
    [0, 0, 0, 0],
    [4968, 114, 4992, 6],
    [48, 4956, 42, 5034],
    [5028, 22, 5028, 2]
    ]

Bp = [
    [36, 4978, 30, 5036],
    [5016, 62, 5010, 4],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0], 
    [0, 0, 0, 0]
    ]

Cp = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [4896, 264, 4896, 24],
    [576, 4416, 216, 5016],
    [4176, 1368, 4464, 72],
    [576, 4032, 504, 4968]
    ]

Zp = [24, 4990, 35, 5030, 1]

R = [1, 3, 35, 9, 27, 30]

# print(Ap)
# print(Bp)
# print(Cp)
# print(Zp)
# print(R)

# sage: Ax
# [ 480 3944  660 4888   12]
# [  24 5016 5030   12 5038]
# [4944  200 4900   40 5036]
# [  24 4990   35 5030    1]
# [  24 4990   35 5030    1]
# [   0    0    0    0    0]

# sage: Bx
# [  24 4990   35 5030    1]
# [   0   90 4947   30 5037]
# [   0 5000   58 5020    2]
# [   0    0    0    0    0]
# [   0    0    0    0    0]
# [   0    0    0    0    0]

# sage: Cx
# [   0    0    0    0    0]
# [3600 4704 3264 1344 4944]
# [2880 4272 2496   48  384]
# [ 720 3888 2016 3312  144]
# [2160  816 1104 1056 4944]
# [ 576 3840  840 4800   24]

# sage: Zx
# (4920, 274, 4815, 85, 5025, 1)

# sage: Rx
# (1, 2, 4, 8, 4, 5028)

### Sagemath ## 

################
### 1. Setup ###
################

p = 71 #Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.
q = p^2-1 #Field size for program, R1CS, and QAP. 

Ax = matrix(ZZ, Ap)
Bx = matrix(ZZ, Bp)
Cx = matrix(ZZ, Cp)
Zx = vector(ZZ, Zp)
Rx = vector(ZZ, R)

Z = IntegerModRing(q)
R.<x> = PowerSeriesRing(Z)

Rax = R(list(Rx*Ax))
Rbx = R(list(Rx*Bx))
Rcx = R(list(Rx*Cx))
Px = Rax * Rbx - Rcx

# [Hx, rem]=polydiv(Px,Zx,q);

# print(Px)
# % 12*x^8 + 4656*x^7 + 4464*x^6 + 120*x^5 + 468*x^4 + 3144*x^3 + 2976*x^2 + 4320

px = Px.polynomial()
zx = R(Zp).polynomial()

Hx = px // zx # 12*x^3 + 4836*x^2 + 384*x + 720
# print(Hx.list())
remainder = px % zx # 0


# P(x)=linear_combination(r,Ax)*linear_combination(r,Bx)-linear_combination(r,Cx)
# Px=(R*Ax)*(R*Bx)-(R*Cx);

# % R*Ax :
# % 30244*x^4 + 65432*x^3 + 30740*x^2 + 74656*x + 20592

# % R*Bx : 
# % 10083*x^4 + 25170*x^3 + 10161*x^2 + 25170*x + 24

# Px : 304950252*x^8 + 1420992336*x^7 + 2264184144*x^6 + 2952578280*x^5 + 4046566068*x^4 + 2028008424*x^3 + 2084804016*x^2 + 500724000*x - 2435040

# % Px=pmod(Px,q)
# % 12*x^8 + 4656*x^7 + 4464*x^6 + 120*x^5 + 468*x^4 + 3144*x^3 + 2976*x^2 + 4320

alpha = 3926
beta = 3604
gamma = 2971
delta = 1357
x_val = 3721

tau = [alpha, beta, gamma, delta, x_val]

# Ax_val=mod(subs(Ax,x,x_val),q);
# Bx_val=mod(subs(Bx,x,x_val),q);
# Cx_val=mod(subs(Cx,x,x_val),q);
# Zx_val=mod(subs(Zx,x,x_val),q);
# Hx_val=mod(subs(Hx,x,x_val),q);

Ax_val = []
Bx_val = []
Cx_val = []
# Zx_val
# Hx_val


for ax in Ax.rows():
    ax_single = R(list(ax))(x_val)
    Ax_val.append(ax_single)

for bx in Bx.rows():
    bx_single = R(list(bx))(x_val)
    Bx_val.append(bx_single)

for cx in Cx.rows():
    cx_single = R(list(cx))(x_val)
    Cx_val.append(cx_single)

Zx_val = R(Zx.list())(x_val)
Hx_val = Hx(x_val)

numGates = len(Ax.columns())
numWires = len(Ax.rows())

print("numGates : {}".format(numGates))
print("numWires : {}".format(numWires))

# numGates : 5
# numWires : 6

# print(Ax_val)
# print(Bx_val)
# print(Cx_val)
# print(Zx_val)
# print(Hx_val)

# Elliptic curve definition G1, G2
# % k=2;
# % % Elliptic curve: y^2=x^3+a*x+0
# % a=1;
# % b=0;
# % p=71; % Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.

EC = EllipticCurve(GF(71), [1,0])
g = EC.points()[12] #(11 : 8 : 1), order is 72, which is max among points

F.<z> = GF(71^2, modulus = x^2 + 1)
# ECExt = EllipticCurve(F,[1,0])
ECExt = EC.base_extend(F)
# ECExt = EC.change_ring(F)
maxpoints = [p for p in ECExt.points() if p.order() == 72]
h = [mp for mp in maxpoints if mp[0] == 60][0] #extended generator

# ECExt2 = EllipticCurve(F,[1,0], gen=h)

pointInf1 = EC.points()[1]
pointInf2 = ECExt.points()[1]


sigma1_1 = [g*alpha, g*beta, g*delta]
sigma1_2 = []
sigma1_3 = []
sigma1_4 = []
sigma1_5 = []

sigma2_1 = [beta*h, gamma*h, delta*h]
sigma2_2 = []

#sigma1_2
for i in range(numGates):
    val = x_val^i % 5040
    sigma1_2.append(val * g)

#sigma1_3

val0 = (beta*Ax_val[0] + alpha*Bx_val[0] + Cx_val[0]) // gamma
val5 = (beta*Ax_val[5] + alpha*Bx_val[5] + Cx_val[5]) // gamma

# print(val0)
# print(val5)

sigma1_3 = [val0 * g, 0, 0, 0, 0, val5 * g]
# print(sigma1_3)

#sigma1_4
val1 = (beta*Ax_val[1] + alpha*Bx_val[1] + Cx_val[1]) // delta
val2 = (beta*Ax_val[2] + alpha*Bx_val[2] + Cx_val[2]) // delta
val3 = (beta*Ax_val[3] + alpha*Bx_val[3] + Cx_val[3]) // delta
val4 = (beta*Ax_val[4] + alpha*Bx_val[4] + Cx_val[4]) // delta

# print(val1)
# print(val2)
# print(val3)
# print(val4)

sigma1_4 = [0, val1 * g, val2 * g, val3 * g, val4 * g, 0]
# print(sigma1_4)

#sigma1_5


for i in range(numGates-1):
    sigma1_5.append(g*(x_val^i * Zx_val // delta))

# print(sigma1_5)

#sigma2-2
for i in range(numGates):
    sigma2_2.append(h*(x_val^i % q))



# print("Sigma1_1 : {}".format(sigma1_1))
# print("Sigma1_2 : {}".format(sigma1_2))
# print("Sigma1_3 : {}".format(sigma1_3))
# print("Sigma1_4 : {}".format(sigma1_4))
# print("Sigma1_5 : {}".format(sigma1_5))
# print("Sigma2_1 : {}".format(sigma2_1))
# print("Sigma2_2 : {}".format(sigma2_2))

# Sigma1_1 : [(24 : 28 : 1), (10 : 67 : 1), (39 : 12 : 1)]
# Sigma1_2 : [(11 : 8 : 1), (23 : 64 : 1), (51 : 28 : 1), (11 : 8 : 1), (23 : 64 : 1)]
# Sigma1_3 : [(0 : 1 : 0), 0, 0, 0, 0, (0 : 1 : 0)]
# Sigma1_4 : [0, (0 : 1 : 0), (0 : 1 : 0), (0 : 1 : 0), (0 : 1 : 0), 0]
# Sigma1_5 : [(0 : 1 : 0), (0 : 1 : 0), (0 : 1 : 0), (0 : 1 : 0)]
# Sigma2_1 : [(61 : 67*z : 1), (9 : 55*z : 1), (32 : 12*z : 1)]
# Sigma2_2 : [(60 : 8*z : 1), (48 : 64*z : 1), (20 : 28*z : 1), (60 : 8*z : 1)]

#TODO : CRS validity check

# if mod(R*Ax_val*R*Bx_val-R*Cx_val,q)==mod(Zx_val*Hx_val,q)
#     disp('CRS is valid')
# else
#     disp('CRS is invalid')
# end

################
### 2. Prove ###
################

#random number created by proover
r = 4106
s = 4565

#Build Proof_A
proof_A = sigma1_1[0]

for i in range(numWires):
    temp = pointInf1    
    for j in range(numGates):
        temp = temp + (Ax[i][j] * sigma1_2[j])    
    proof_A = proof_A + (Rx[i] * temp)
proof_A = proof_A + (r * sigma1_1[2])

# print(proof_A)

#Build proof_B
proof_B = sigma2_1[0]
for i in range(numWires):
    temp = pointInf2   
    for j in range(numGates):
        temp = temp + (Bx[i][j] * sigma2_2[j])    
    proof_B = proof_B + (Rx[i] * temp)
proof_B = proof_B + (s * sigma2_1[2])

# print(proof_B)

#Build temp_proof_B
temp_proof_B = sigma1_1[1]
for i in range(numWires):
    temp = pointInf1
    for j in range(numGates):
        temp = temp + (Bx[i][j] * sigma1_2[j])    
    temp_proof_B = temp_proof_B + (Rx[i] * temp)
temp_proof_B = temp_proof_B + (s * sigma1_1[2])

# print(temp_proof_B)

#Build proof_C
proof_C = (s * proof_A) + (r * temp_proof_B) - (r*s*sigma1_1[2])

for i in range(1,numGates-1):
    proof_C = proof_C + (Rx[i] * sigma1_4[i])

for i in range(numGates-1):
    proof_C = proof_C + (Hx[i] * sigma1_5[i])

proof = [proof_A, proof_B, proof_C]


#################
### 3. Verify ###
#################

def weil(point1, point2):
    val = EC.isomorphism_to(ECExt)(point1).weil_pairing(point2, 72)
    return val

LHS = weil(proof_A, proof_B)
RHS = weil(sigma1_1[0], sigma2_1[0])

temp = pointInf1

for i in [0, numWires-1]:
  temp = temp + Rx[i]*sigma1_3[i]

RHS = RHS * weil(temp, sigma2_1[1])
RHS = RHS * weil(proof[2], sigma2_1[2])

print(LHS)
print(RHS)

print("Verification result (RHS == LHS)? : {}".format(RHS == LHS))