q = 11
Fq = GF(q)

# F.<z> = GF(5^2, modulus = x^2 + 2)
# print(F)

# Elliptic Curve defined by y^2 = x^3 + 4 over Finite Field of size 11
E = EllipticCurve(Fq, [0,4])

# #E(Fq) = 12 (order of E)
# num_of_points_E = len(E.points())
order_E = E.order()
print(order_E)

#factorization
factorized_order = order_E.factor() # 2^2 * 3
print(factorized_order)

# r-torsion(degree of E)
r = E.degree() # r = 3

# find smallest embedding degree of E; k
smallest_isogency = E.isogenies_prime_degree()[0] #finding possible isogencies
k = smallest_isogency.degree()

# We will using k as F_q^k with x + 5
kernal_poly = smallest_isogency.kernel_polynomial() # x+5
print(kernal_poly)

# Fr with x^2+1
F.<z> = GF(11^2, modulus = x^2 + 1)
EFr = EllipticCurve(F, [0,4])

# E[r] = {P in E: [r]P = O}
subgroup_E3 = [P for P in EFr if 3 * P == 0]
print(subgroup_E3)

# twist of E, d = {2,3,4,6}, here d = 2

#Frd.<z> = GF(11^(2/2), modulus = x^2 + 1)
#EFrd = EllipticCurve(Frd, [0,4])

tE = E.quadratic_twist()
print(tE.points())

## Coset Related ##

#checking the max order
max_order = max([P.order() for P in E.points()])

#extract random point which order equals to max_order
P = EFr.points()[4]

#calculate h, coset order
h = Integer(EFr.order()/r^2)

#coset point's order equals to r
(h*P).order() == r

#making coset list
#rE(Fq^k) = rE = {[r]P: P in E(Fq^k)}
coset_EFr_points = list(dict.fromkeys([r*P for P in EFr.points()]))

#lenth of coset equals to h
len(coset_EFr_points) == h