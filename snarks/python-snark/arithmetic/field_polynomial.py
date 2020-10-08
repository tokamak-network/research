from .field import FQ, bn128_Field
from .field_properties import field_properties

class FieldPolynomial:
    field_modulus = None
    def __init__(self):
        pass
        
        if self.field_modulus is None:
            raise AttributeError("Field modulus hasn't been specified")
        """
        if self.field is None:
            raise AttributeError("Field hasn't been specified")
        """
        self.s = 1
        self.t = self.field_modulus - self.s

        # TO find multiplicative subgroup root of unity lower than fqVal
        # s : group size(order)
        # t : root of unity
        while self.t % 2 != 1:
            self.s = self.s + 1
            self.t = self.t >> 1

        rem = self.t
        s = self.s - 1

        self.w = { s : bn128_Field(5)**rem }
        self.wi = { s :  bn128_Field(1) / self.w[s] }

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
            r = bn128_Field(1)
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
        return t**m - bn128_Field(1)

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

        z = tm - bn128_Field(1)
        # print("z : ", z)
        l = z / bn128_Field(m)
        # print("l : ", l)

        for i in range(m):
            u[i] = l / (t - self.roots[bits][i])
            l = l * omega

        return u


class bn128_FieldPolynomial(FieldPolynomial):
    field_modulus = field_properties["bn128"]["q"]