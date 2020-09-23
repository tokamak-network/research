from __future__ import absolute_import
from typing import cast, List, Tuple, Sequence, Union
from .field import FQ, FR

from math import log2

IntOrFQ = Union[int, "FQ"]

field_modulus = (
    21888242871839275222246405745257275088548364400416034343698204186575808495617
)

class Polfield:
    def __init__(self):
        # print("hello!")

        self.s = 1
        self.t = field_modulus - self.s

        # TO find multiplicative subgroup root of unity lower than fqVal
        # s : group size(order)
        # t : root of unity
        while self.t % 2 != 1:
            self.s = self.s + 1
            self.t = self.t >> 1

        rem = self.t
        s = self.s - 1
        # print("rem : ", rem)
        # print("s : ", s)

        self.w = { s : FR(5)**rem }
        self.wi = { s :  FR(1) / self.w[s] }

        n = s - 1
        while n >= 0:
            self.w.update({n : self.w[n+1]**2})
            self.wi.update({n : self.wi[n+1]**2})
            n -= 1

        self.roots = {}
        self._set_roots(15)

    def _set_roots(self, n: int):
        self.roots = {}
        for i in reversed(range(0, n+1)):
            r = FR(1)
            nroots = 1 << i
            rootsi = {}

            for j in range(nroots):
                rootsi.update({j:r})
                r = r * self.w[i]

            self.roots.update({i : rootsi})

    def compute_vanishing_polynomial(self, bits: int, t: FQ):
        # t : toxic waste(셋업 마치면 사라져야되는 값)
        # m : constraints 수에 근접(A, B, C 행렬의 row 갯수), 무조껀 짝수
        # -> taget polynomial H * T = A*u + B*u - C*u
        m = 1 << bits
        return t**m - FR(1)

    def evaluate_lagrange_polynomials(self, bits: int, t: FQ) -> "Dict":
        m = 1 << bits
        tm = t ** m

        # print("m : "  , m )
        # print("t : "  , t )
        # print("t^m : ", tm)

        u = dict()
        for i in range(m):
            u.update( {i : 0} )
        self._set_roots(bits)
        omega = self.w[bits]

        #TODO : if tm == 1

        z = tm - FR(1)
        # print("z : ", z)
        l = z / FR(m)
        # print("l : ", l)

        for i in range(m):
            u[i] = l / (t - self.roots[bits][i])
            l = l * omega

        return u

    @classmethod
    def log2(cls, V: int) -> "Int":
        if V & 0xFFFF0000 != 0:
            a = 16
            V &= 0xFFFF0000
        else:
            a = 0

        if V & 0xFF00FF00 != 0:
            b = 8
            V &= 0xFF00FF00
        else:
            b = 0

        if V & 0xF0F0F0F0 != 0:
            c = 4
            V &= 0xF0F0F0F0
        else:
            c = 0

        if V & 0xCCCCCCCC != 0:
            d = 2
            V &= 0xCCCCCCCC
        else:
            d = 0

        if V & 0xAAAAAAAA != 0:
            e = 1
        else:
            e = 0

        return a | b | c | d | e


# if __name__ == "__main__":
#     pf = Polfield()
#     print(pf.w[0])
#     print(len(pf.w))
#     print(pf.roots[0])
#     print(pf.roots[1])
#     t = FR(5)
#     evaluated = pf.evaluate_lagrange_polynomials(7, t)
#     print("0 : ", evaluated[0])
#     print("1 : ", evaluated[1])
#     print("len: ", len(evaluated))
