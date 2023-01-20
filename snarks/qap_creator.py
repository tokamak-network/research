# Polynomials are stored as arrays, where the ith element in
# the array is the ith degree coefficient

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

# Make a polynomial which is zero at {1, 2 ... total_pts}, except
# for `point_loc` where the value is `height`
# j번째 라그랑주 L_j(x) 다항식 계산 함수
def mk_singleton(point_loc, height, total_pts):
    fac = 1
    # 라그랑주의 (x_j,y_j)중, x_j는 1,2,3 ... 으로 1부터 하나씩 커지고 있고, y_j값은 함수 파라미터로부터 받아옴
    for i in range(1, total_pts + 1):
        if i != point_loc:
            fac *= point_loc - i
    # L_j의 분모(fac, x_j-x_(j-1)와 계수(y_i) 계산
    o = [height * 1.0 / fac]
    # L_j의 분자(x-x_j ... ) 계산
    for i in range(1, total_pts + 1):
        if i != point_loc:
            # (x-x_0)(x-x_1) ... (x-x_(j-1))(x_x_(j+1))..(x-x_k) <- 라그랑주 분자 계산
            o = multiply_polys(o, [-i, 1])
    return o

# Assumes vec[0] = p(1), vec[1] = p(2), etc, tries to find p,
# expresses result as [deg 0 coeff, deg 1 coeff...]
def lagrange_interp(vec):
    o = []
    # 라그랑주의 x값을 1,2,3 ... 으로 씀
    for i in range(len(vec)):
        # 각각의 라그랑주를 더함
        o = add_polys(o, mk_singleton(i + 1, vec[i], len(vec)))
    for i in range(len(vec)):
        assert abs(eval_poly(o, i + 1) - vec[i] < 10**-10), \
            (o, eval_poly(o, i + 1), i+1)
    return o

def transpose(matrix):
    return list(map(list, zip(*matrix)))

# A, B, C = matrices of m vectors of length n, where for each
# 0 <= i < m, we want to satisfy A[i] * B[i] - C[i] = 0
def r1cs_to_qap(A, B, C):
    # A, B, C 매트릭스의 각 row를 라그랑주 보간법 수행
    A, B, C = transpose(A), transpose(B), transpose(C)
    new_A = [lagrange_interp(a) for a in A]
    new_B = [lagrange_interp(b) for b in B]
    new_C = [lagrange_interp(c) for c in C]
    # (x-1)(x-2)(x-3)..(x-k) 다항식 계산(Z)
    Z = [1]
    for i in range(1, len(A[0]) + 1):
        Z = multiply_polys(Z, [-i, 1])
    return (new_A, new_B, new_C, Z)

def create_solution_polynomials(r, new_A, new_B, new_C):

    # r = [r1(x), r2(x), r3(x), r4(x), r5(x), r6(x)]
    # A(x) = [a1(x), a2(x), a3(x), a4(x), a5(x), a6(x)]
    # B(x) = [b1(x), b2(x), b3(x), b4(x), b5(x), b6(x)]
    # C(x) = [c1(x), c2(x), c3(x), c4(x), c5(x), c6(x)]

    # Apoly = r.A(x)
    #       = r1(x)*a1(x) + r2(x)*a2(x) + ... + r6(x)*a6(x)
    Apoly = []
    for rval, a in zip(r, new_A):
        Apoly = add_polys(Apoly, multiply_polys([rval], a))

    # Bpoly = r.B(x)
    # Bpoly = r1(x)*b1(x) + r2(x)*b2(x) + ... + r6(x)*b6(x)
    Bpoly = []
    for rval, b in zip(r, new_B):
        Bpoly = add_polys(Bpoly, multiply_polys([rval], b))

    # Cpoly = r.C(x)
    # Cpoly = r1(x)*c1(x) + r2(x)*c2(x) + ... + r6(x)*c6(x)
    Cpoly = []
    for rval, c in zip(r, new_C):
        Cpoly = add_polys(Cpoly, multiply_polys([rval], c))

    # o = r.A(x)*r.B(x)-r.C(x)
    o = subtract_polys(multiply_polys(Apoly, Bpoly), Cpoly)
    for i in range(1, len(new_A[0]) + 1):
        assert abs(eval_poly(o, i)) < 10**-10, (eval_poly(o, i), i)

    # Return r.A(x), r.B(x), r.C(x), r.A(x)*r.B(x)-r.C(x) = o
    return Apoly, Bpoly, Cpoly, o

def create_divisor_polynomial(sol, Z):
    quot, rem = div_polys(sol, Z)
    for x in rem:
        assert abs(x) < 10**-10
    return quot

r = [1, 3, 35, 9, 27, 30]
A = [[0, 1, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0],
     [0, 1, 0, 0, 1, 0],
     [5, 0, 0, 0, 0, 1]]
B = [[0, 1, 0, 0, 0, 0],
     [0, 1, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 0]]
C = [[0, 0, 0, 1, 0, 0],
     [0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 1],
     [0, 0, 1, 0, 0, 0]]

Ap, Bp, Cp, Z = r1cs_to_qap(A, B, C)
print('Ap')
for x in Ap: print(x)
print('Bp')
for x in Bp: print(x)
print('Cp')
for x in Cp: print(x)
print('Z')
print(Z)
Apoly, Bpoly, Cpoly, sol = create_solution_polynomials(r, Ap, Bp, Cp)
print('Apoly(A(x))')
print(Apoly)
print('Bpoly(B(x))')
print(Bpoly)
print('Cpoly(C(x))')
print(Cpoly)
print('Sol(A(x)*B(x)-C(x))')
print(sol)
print('Z cofactor, H')
# A(x)*B(x)-C(x) = H*Z
# <==>
# (A(x)*B(x)-C(x)) / Z = H
# <==>
# (A(x)*B(x)-C(x)) / (x-1)(x-2)(x-3)..(x-k) = H
print(create_divisor_polynomial(sol, Z))
