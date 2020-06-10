"""
This code is copied from https://github.com/ethereum/py_ecc/blob/master/py_ecc/bn128/bn128_curve.py
Author is Vitalik Buterin.
Unfortunately the field modulus is not generic in this implementation, hence we had to copy the file.
All changes from our side are denoted with #CHANGE.
"""

from __future__ import absolute_import

from typing import cast, List, Tuple, Sequence, Union


# The prime modulus of the field
# field_modulus = 21888242871839275222246405745257275088696311157297823662689037894645226208583
field_modulus = (
    21888242871839275222246405745257275088548364400416034343698204186575808495617
)
# CHANGE: Changing the modulus to the embedded curve

field_properties = {
    "bn128": {
        "field_modulus": 21888242871839275222246405745257275088696311157297823662689037894645226208583,  # noqa: E501
        "fq2_modulus_coeffs": (1, 0),
        "fq12_modulus_coeffs": (82, 0, 0, 0, 0, 0, -18, 0, 0, 0, 0, 0),  # Implied + [1]
    },
    "bls12_381": {
        "field_modulus": 4002409555221667393417789825735904156556882819939007885332058136124031650490837864442687629129015664037894272559787,  # noqa: E501
        "fq2_modulus_coeffs": (1, 0),
        "fq12_modulus_coeffs": (2, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0),  # Implied + [1]
    },
}   # type: Field_Properties

# See, it's prime!
assert pow(2, field_modulus, field_modulus) == 2

IntOrFQ = Union[int, "FQ"]

# The modulus of the polynomial in this representation of FQ12
# FQ12_MODULUS_COEFFS = (82, 0, 0, 0, 0, 0, -18, 0, 0, 0, 0, 0)  # Implied + [1]
# FQ2_MODULUS_COEFFS = (1, 0)
# CHANGE: No need for extended  in this case

# Extended euclidean algorithm to find modular inverses for
# integers
def inv(a: int, n: int) -> int:
    if a == 0:
        return 0
    lm, hm = 1, 0
    num = a if isinstance(a, int) else a.n
    low, high = num % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n


# Utility methods for polynomial math
def deg(p: Sequence[Union[int, "FQ"]]) -> int:
    d = len(p) - 1
    print("start : ", p)
    while p[d] == 0 and d:
        print("")
        print("d    : ", d)
        print("p    : ", p)
        print("p[d] : ", p[d])
        d -= 1
    return d


def poly_rounded_div(a: Sequence[IntOrFQ],
                     b: Sequence[IntOrFQ]) -> Tuple[IntOrFQ, ...]:
    dega = deg(a)
    degb = deg(b)
    temp = [x for x in a]
    o = [0 for x in a]
    for i in range(dega - degb, -1, -1):
        o[i] += int(temp[degb + i] / b[degb])
        for c in range(degb + 1):
            temp[c + i] -= o[c]
    return cast(Tuple[IntOrFQ, ...], tuple(o[:deg(o) + 1]))



# A class for field elements in FQ. Wrap a number in this class,
# and it becomes a field element.
class FQ(object):
    n = None  # type: int

    def __init__(self, val: IntOrFQ) -> None:
        if isinstance(val, FQ):
            self.n = val.n
        else:
            self.n = val % field_modulus
        assert isinstance(self.n, int)

    def __add__(self, other: IntOrFQ) -> "FQ":
        on = other.n if isinstance(other, FQ) else other
        return FQ((self.n + on) % field_modulus)

    def __mul__(self, other: IntOrFQ) -> "FQ":
        on = other.n if isinstance(other, FQ) else other
        return FQ((self.n * on) % field_modulus)

    def __rmul__(self, other: IntOrFQ) -> "FQ":
        return self * other

    def __radd__(self, other: IntOrFQ) -> "FQ":
        return self + other

    def __rsub__(self, other: IntOrFQ) -> "FQ":
        on = other.n if isinstance(other, FQ) else other
        return FQ((on - self.n) % field_modulus)

    def __sub__(self, other: IntOrFQ) -> "FQ":
        on = other.n if isinstance(other, FQ) else other
        return FQ((self.n - on) % field_modulus)

    def __div__(self, other: IntOrFQ) -> "FQ":
        on = other.n if isinstance(other, FQ) else other
        assert isinstance(on, int)
        return FQ(self.n * inv(on, field_modulus) % field_modulus)

    def __truediv__(self, other: IntOrFQ) -> "FQ":
        return self.__div__(other)

    def __rdiv__(self, other: IntOrFQ) -> "FQ":
        on = other.n if isinstance(other, FQ) else other
        assert isinstance(on, int), on
        return FQ(inv(self.n, field_modulus) * on % field_modulus)

    def __rtruediv__(self, other: IntOrFQ) -> "FQ":
        return self.__rdiv__(other)

    def __pow__(self, other: int) -> "FQ":
        if other == 0:
            return FQ(1)
        elif other == 1:
            return FQ(self.n)
        elif other % 2 == 0:
            return (self * self) ** (other // 2)
        else:
            return ((self * self) ** int(other // 2)) * self

    def __eq__(
        self, other: IntOrFQ
    ) -> bool:  # type:ignore # https://github.com/python/mypy/issues/2783 # noqa: E501
        if isinstance(other, FQ):
            return self.n == other.n
        else:
            return self.n == other

    def __ne__(
        self, other: IntOrFQ
    ) -> bool:  # type:ignore # https://github.com/python/mypy/issues/2783 # noqa: E501
        return not self == other

    def __neg__(self) -> "FQ":
        return FQ(-self.n)

    def __repr__(self) -> str:
        return repr(self.n)

    def __int__(self) -> int:
        return self.n

    @classmethod
    def one(cls) -> "FQ":
        return cls(1)

    @classmethod
    def zero(cls) -> "FQ":
        return cls(0)


class FQP(object):
    """
    A class for elements in polynomial extension fields
    """
    degree = 0
    field_modulus = None

    # coeffs는 배열, 각 coeffs는 FQ타입이어야 함
    # modulus_coeffs또한 배열, 또한 모두 FQ타입이여야 함, 다만 modulus_coeffs는 체의 스펙에 따라 모두 상수로 이미 결정되어 있음
    # https://github.com/ethereum/py_ecc/blob/master/py_ecc/fields/field_properties.py#L23-L34
    # TODO : coeffs, modulus_coeffs --> type checking구현 필요
    def __init__(self, coeffs, modulus_coeffs = ()):
        if self.field_modulus is None:
            raise Exception("Error")
        if len(coeffs) != len(modulus_coeffs):
            raise Exception("Error")

        self.coeffs = tuple(coeffs)
        self.modulus_coeffs = tuple(modulus_coeffs)

        # modulus coeffs의 크기가 degree(차원)이 됨
        self.degree = len(modulus_coeffs)

    # 다항식의 덧샘
    def __add__(self, other):
        return type(self)([x + y for x, y in zip(self.coeffs, other.coeffs)])

    # 다항식의 뺄셈
    def __sub__(self, other):
        return type(self)([x - y for x, y in zip(self.coeffs, other.coeffs)])

    # 다항식의 곱셈
    def __mul__(self, other):
        # TODO : other 타잎이 확대체, 체, 인트 배열인지 확인하고 타입 전환
        if isinstance(other, FQP):
            b = [FQ(0) for i in range(self.degree * 2 - 1)]
            for i in range(self.degree):
                for j in range(self.degree):
                    b[i + j] += self.coeffs[i] * other.coeffs[j]

            # GF내에서 다항식의 곱의 결과로 나오는 출력다항식의 최고차수 (len(b))는
            # 기약다항식의 최고차수 (self.degree)보다 커서는 안됩니다.
            # 예로, 코드의 init을보면 타켓다항식의 degree와 기약다항식의 degree를 비교하여
            # 예외처리를 해주는 조건문이 하나 있네요.
            # 그리고 이러한 이유 때문에, 언급하신 252~255 라인이 사용되는 것 같네요.
            # 아래의 라인은 다음의 링크에 나오는 중학교 다항식의 나눗셈 방법을 그대로 구현한것입니다.
            # (https://mathbang.net/313)
            while len(b) > self.degree:
                exp, top = len(b) - self.degree - 1, b.pop()
                for i in range(self.degree):
                    b[exp + i] -= top * FQ(self.modulus_coeffs[i])

            return type(self)(b)

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        if isinstance(other, FQ):
            return FQP([c / other for c in self.coeffs], self.modulus_coeffs)
        if isinstance(other, FQP):
            # TODO : FQP.inv() should be implemented
            return self * other.inv()
        else:
            raise TypeError(
                "Expected an int or FQ object or FQP object, but got object of type {}"
                .format(type(other))
            )
    def __truediv__(self, other):
        return self.__div__(other)

    def __pow__(self, other):
        if other == 0:
            return type(self)([1] + [0] * (self.degree - 1))
        elif other == 1:
            return type(self)(self.coeffs)
        elif other % 2 == 0:
            return (self * self) ** (other // 2)
        else:
            return ((self * self) ** int(other // 2)) * self

    def inv(self):
        lm, hm = (
            [1] + [0] * self.degree,
            [0] * (self.degree +1),
        )

        low, high = (
            list(self.coeffs + (0,)),
            list(self.modulus_coeffs + (1,))
        )

        while deg(low):
            r = cast(List[IntOrFQ], list(poly_rounded_div(high, low)))
            r += [0] * (self.degree + 1 - len(r))
            nm = [x for x in hm]
            new = [x for x in high]

            if len(lm) != self.degree + 1:
                raise Exception("Length of lm is not {}".format(self.degree + 1))
            elif len(hm) != self.degree + 1:
                raise Exception("Length of hm is not {}".format(self.degree + 1))
            elif len(nm) != self.degree + 1:
                raise Exception("Length of nm is not {}".format(self.degree + 1))
            elif len(low) != self.degree + 1:
                raise Exception("Length of low is not {}".format(self.degree + 1))
            elif len(high) != self.degree + 1:
                raise Exception("Length of high is not {}".format(self.degree + 1))
            elif len(new) != self.degree + 1:
                raise Exception("Length of new is not {}".format(self.degree + 1))

            for i in range(self.degree + 1):
                for j in range(self.degree + 1 - i):
                    nm[i + j] -= lm[i] * int(r[j])
                    new[i + j] -= low[i] * int(r[j])
            lm, low, hm, high = nm, new, lm, low

        return type(self)(lm[:self.degree]) / low[0]

    def __repr__(self):
        return repr(self.coeffs)

    def __eq__(self, other):
        for c1, c2 in zip(self.coeffs, other.coeffs):
            if c1 != c2:
                return False
        return True

    def __neg__(self):
        return type(self)([-c for c in self.coeffs])

    @classmethod
    def one(cls):
        return cls([1] + [0] * (cls.degree-1))

    @classmethod
    def zero(cls):
        return cls([0] * cls.degree)


class FQ2(FQP):
    degree = 2
    field_modulus = field_properties["bn128"]["field_modulus"]
    FQ2_MODULUS_COEFFS = field_properties["bn128"]["fq2_modulus_coeffs"]

    def __init__(self, coeffs):
        super().__init__(coeffs, self.FQ2_MODULUS_COEFFS)


class FQ12(FQP):
    degree = 12
    field_modulus = field_properties["bn128"]["field_modulus"]
    FQ12_MODULUS_COEFFS = field_properties["bn128"]["fq12_modulus_coeffs"]

    def __init__(self, coeffs):
        super().__init__(coeffs, self.FQ12_MODULUS_COEFFS)
