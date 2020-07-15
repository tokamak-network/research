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
    def affine(self, p) -> "BN128":
        if p == self.zero:
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

    def double(self):
        return

    def add(self):
        return

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

    # mul_scalar test : test failed
    # p_mul = bn.mul_scalar(p, 151)
    # print(p_mul)
