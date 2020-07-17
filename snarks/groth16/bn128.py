from typing import cast, List, Tuple, Sequence, Union
from field import FQ, FR

IntOrFQ = Union[int, "FQ"]

class BN128:
    def __init__(self, g):
        self.g = g
        if len(g) == 2:
            this.g.append(FQ(1))

        self.zero = [FQ(0), FQ(1), FQ(0)]

    # jacobian coordinate
    @classmethod
    def affine(cls, p) -> "BN128":
        if p == [FQ(0), FQ(1), FQ(0)]:
            return self.zero
        else:
            z_inv = 1 / p[0]
            z2_inv = z_inv ** 2
            z3_inv = z_inv * z2_inv
            print("z_inv  : ", z_inv)
            print("z2_inv : ", z2_inv)
            print("z3_inv : ", z3_inv)

            res = [None]*3

            res[0] = p[0] * z2_inv
            res[1] = p[1] * z3_inv
            res[2] = FQ(1)

            return res

    @classmethod
    def double(cls, p):
        res = [None] * 3
        if p == [FQ(0), FQ(1), FQ(0)]:
            return p

        # A = X1^2
        # B = Y1^2
        # C = B^2
        A = FQ(p[0]) ** 2
        B = FQ(p[1]) ** 2
        C = B ** 2

        # D = 2 * ((X1 + B)^2 - A - C)
        D = 2 * (((p[0] + B) ** 2) - A - C)
        E = 3 * A
        F = E ** 2

        res[0] = F - 2 * D
        eightC = C * 8

        # Y3 = E * (D - X3) - 8 * C
        res[1] = E * (D - res[0]) - eightC

        Y1Z1 = p[1] * p[2]
        res[2] = Y1Z1 * 2

        return res

    @classmethod
    def add(cls, p1, p2):
        if p1 == [FQ(0), FQ(1), FQ(0)]: return p2
        if p2 == [FQ(0), FQ(1), FQ(0)]: return p1

        res = [None] * 3

        Z1Z1 = p1[2] ** 2
        Z2Z2 = p2[2] ** 2

        U1 = p1[0] * Z2Z2 #U1 = X1 * Z2Z2
        U2 = p2[0] * Z1Z1 #U2 = X2 * Z1Z1

        Z1_cubed = p1[2] * Z1Z1
        Z2_cubed = p2[2] * Z2Z2

        S1 = p1[1] * Z2_cubed #S1 = Y1 * Z2 * Z2Z2
        S2 = p[1] * Z1_cubed #S2 = Y2 * Z1 * Z1Z1

        if U1 == U2 and S1 == S2:
            cls.double(p1)

        H = U2 - U1

        S2_minus_S1 = S2 - S1

        I = (H*2) ** 2
        J = H * I

        r = S2_minus_S1 + S2_minus_S1
        V = U1 * I

        S1_J = S1 * J

        # X3 = r^2 - J - 2 * V
        # Y3 = r * (V-X3)-2*S1*J
        # Z3 = ((Z1+Z2)^2-Z1Z1-Z2Z2) * H
        res[0] = r ** 2 - J - 2*V
        res[1] = r * (V - res[0]) - (2 * S1_J)
        res[2] = ((p1[2] + p2[2])**2 - Z1Z1 - Z2Z2) * H

        return res

    # def mul_scalar(self, base, e)-> "BN128":
    #     res = FQ(0)
    #     rem = FQ(e)
    #     exp = base
    #
    #     while rem == FQ(0):
    #         if rem + FQ(0) == FQ(1):
    #             res = res + exp
    #         exp = exp ** 2
    #         rem = rem >> 1
    #
    #     return res

if __name__ == "__main__":
    # affine test : it works!
    p = [FQ(1), FQ(2), FQ(1)]
    bn = BN128(p)
    p_affine = bn.affine(p)
    print(p_affine)

    # double() test : it works!
    double_p = bn.double(p)
    print(bn.double(p))
    print(bn.double(double_p))

    # add() test : it works!
    print("bn.add(p, p) : ", bn.add(double_p, p))

    # mul_scalar test : test failed
    # p_mul = bn.mul_scalar(p, 151)
    # print(p_mul)
