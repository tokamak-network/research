"""
This code is copied from https://github.com/ethereum/py_ecc/blob/master/py_ecc/bn128/bn128_curve.py
Author is Vitalik Buterin.
Unfortunately the field modulus is not generic in this implementation, hence we had to copy the file.
All changes from our side are denoted with #CHANGE.
"""

from __future__ import absolute_import
from typing import cast, List, Tuple, Sequence, Union, TypeVar, Type


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

T_FQ = TypeVar('T_FQ', bound="FQ")
T_FQP = TypeVar('T_FQP', bound="FQP")
T_FQ2 = TypeVar('T_FQ2', bound="FQ2")
T_FQ12 = TypeVar('T_FQ12', bound="FQ12")
IntOrFQ = Union[int, T_FQ]

# The modulus of the polynomial in this representation of FQ12
# FQ12_MODULUS_COEFFS = (82, 0, 0, 0, 0, 0, -18, 0, 0, 0, 0, 0)  # Implied + [1]
# FQ2_MODULUS_COEFFS = (1, 0)
# CHANGE: No need for extended  in this case

# Extended euclidean algorithm to find modular inverses for
# integers
def prime_field_inv(a: int, n: int) -> int:
    """
    Extended euclidean algorithm to find modular inverses for integers
    """
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n


# Utility methods for polynomial math
def deg(p: Sequence[Union[int, "FQ"]]) -> int:
    d = len(p) - 1
    while p[d] == 0 and d:
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
    """
    A class for field elements in FQ. Wrap a number in this class,
    and it becomes a field element.
    """
    n = None  # type: int
    field_modulus = field_properties["bn128"]["field_modulus"]

    def __init__(self: T_FQ, val: IntOrFQ) -> None:
        if self.field_modulus is None:
            raise AttributeError("Field Modulus hasn't been specified")

        if isinstance(val, FQ):
            self.n = val.n
        elif isinstance(val, int):
            self.n = val % self.field_modulus
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(val))
            )

    def __add__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((self.n + on) % self.field_modulus)

    def __mul__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((self.n * on) % self.field_modulus)

    def __rmul__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self * other

    def __radd__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self + other

    def __rsub__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((on - self.n) % self.field_modulus)

    def __sub__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)((self.n - on) % self.field_modulus)

    def __div__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)(
            self.n * prime_field_inv(on, self.field_modulus) % self.field_modulus
        )

    def __truediv__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self.__div__(other)

    def __rdiv__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        if isinstance(other, FQ):
            on = other.n
        elif isinstance(other, int):
            on = other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

        return type(self)(
            prime_field_inv(self.n, self.field_modulus) * on % self.field_modulus
        )

    def __rtruediv__(self: T_FQ, other: IntOrFQ) -> T_FQ:
        return self.__rdiv__(other)

    def __pow__(self: T_FQ, other: int) -> T_FQ:
        if other == 0:
            return type(self)(1)
        elif other == 1:
            return type(self)(self.n)
        elif other % 2 == 0:
            return (self * self) ** (other // 2)
        else:
            return ((self * self) ** int(other // 2)) * self

    def __eq__(self: T_FQ, other: IntOrFQ) -> bool:
        if isinstance(other, FQ):
            return self.n == other.n
        elif isinstance(other, int):
            return self.n == other
        else:
            raise TypeError(
                "Expected an int or FQ object, but got object of type {}"
                .format(type(other))
            )

    def __ne__(self: T_FQ, other: IntOrFQ) -> bool:
        return not self == other

    def __neg__(self: T_FQ) -> T_FQ:
        return type(self)(-self.n)

    def __repr__(self: T_FQ) -> str:
        return repr(self.n)

    def __int__(self: T_FQ) -> int:
        return self.n

    @classmethod
    def one(cls: Type[T_FQ]) -> T_FQ:
        return cls(1)

    @classmethod
    def zero(cls: Type[T_FQ]) -> T_FQ:
        return cls(0)

int_types_or_FQ = (int, FQ)


class FQP(object):
    """
    A class for elements in polynomial extension fields
    """
    degree = 0
    field_modulus = None  # type: int

    def __init__(self,
                 coeffs: Sequence[IntOrFQ],
                 modulus_coeffs: Sequence[IntOrFQ] = ()) -> None:
        if self.field_modulus is None:
            raise AttributeError("Field Modulus hasn't been specified")

        if len(coeffs) != len(modulus_coeffs):
            raise Exception(
                "coeffs and modulus_coeffs aren't of the same length"
            )
        # Encoding all coefficients in the corresponding type FQ
        self.FQP_corresponding_FQ_class = type(
            "FQP_corresponding_FQ_class",
            (FQ,),
            {'field_modulus': self.field_modulus}
        )  # type: Type[FQ]
        self.coeffs = tuple(
            self.FQP_corresponding_FQ_class(c) for c in coeffs
        )  # type: Tuple[IntOrFQ, ...]
        # The coefficients of the modulus, without the leading [1]
        self.modulus_coeffs = tuple(modulus_coeffs)  # type: Tuple[IntOrFQ, ...]
        # The degree of the extension field
        self.degree = len(self.modulus_coeffs)

    def __add__(self: T_FQP, other: T_FQP) -> T_FQP:
        if not isinstance(other, type(self)):
            raise TypeError(
                "Expected an FQP object, but got object of type {}"
                .format(type(other))
            )

        return type(self)([x + y for x, y in zip(self.coeffs, other.coeffs)])

    def __sub__(self: T_FQP, other: T_FQP) -> T_FQP:
        if not isinstance(other, type(self)):
            raise TypeError(
                "Expected an FQP object, but got object of type {}"
                .format(type(other))
            )

        return type(self)([x - y for x, y in zip(self.coeffs, other.coeffs)])

    def __mul__(self: T_FQP, other: Union[int, T_FQ, T_FQP]) -> T_FQP:
        if isinstance(other, int_types_or_FQ):
            return type(self)([c * other for c in self.coeffs])
        elif isinstance(other, FQP):
            b = [self.FQP_corresponding_FQ_class(0) for i in range(self.degree * 2 - 1)]
            for i in range(self.degree):
                for j in range(self.degree):
                    b[i + j] += self.coeffs[i] * other.coeffs[j]
            while len(b) > self.degree:
                exp, top = len(b) - self.degree - 1, b.pop()
                for i in range(self.degree):
                    b[exp + i] -= top * self.FQP_corresponding_FQ_class(self.modulus_coeffs[i])
            return type(self)(b)
        else:
            raise TypeError(
                "Expected an int or FQ object or FQP object, but got object of type {}"
                .format(type(other))
            )

    def __rmul__(self: T_FQP, other: Union[int, T_FQP]) -> T_FQP:
        return self * other

    def __div__(self: T_FQP, other: Union[int, T_FQP]) -> T_FQP:
        if isinstance(other, int_types_or_FQ):
            return type(self)([c / other for c in self.coeffs])
        elif isinstance(other, FQP):
            return self * other.inv()
        else:
            raise TypeError(
                "Expected an int or FQ object or FQP object, but got object of type {}"
                .format(type(other))
            )

    def __truediv__(self: T_FQP, other: Union[int, T_FQP]) -> T_FQP:
        return self.__div__(other)
    """
    def __pow__(self: T_FQP, other: int) -> T_FQP:
        if other == 0:
            return type(self)([1] + [0] * (self.degree - 1))
        elif other == 1:
            return type(self)(self.coeffs)
        elif other % 2 == 0:
            return (self * self) ** (other // 2)
        else:
            return ((self * self) ** int(other // 2)) * self
    """

    def __pow__(self: T_FQP, other: int) -> T_FQP:
        if other == 0:
            return type(self)([1] + [0] * (self.degree - 1))
        elif other == 1:
            return type(self)(self.coeffs)
        
        n = [int(x) for x in bin(other)[2:]]
        if len(n) == 0:
            return type(self)([1] + [0] * (self.degree - 1))

        res = self;

        for i in range(1, len(n)):
            res = res * res
            if n[i] != 0:
                res = res * self
        return res;
        

    # Extended euclidean algorithm used to find the modular inverse
    def inv(self: T_FQP) -> T_FQP:
        lm, hm = (
            [1] + [0] * self.degree,
            [0] * (self.degree + 1),
        )
        low, high = (
            # Ignore mypy yelling about the inner types for  the tuples being incompatible
            cast(List[IntOrFQ], list(self.coeffs + (0,))),
            cast(List[IntOrFQ], list(self.modulus_coeffs + (1,))),
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

    def __repr__(self: T_FQP) -> str:
        return repr(self.coeffs)

    def __eq__(self: T_FQP, other: T_FQP) -> bool:     # type: ignore # https://github.com/python/mypy/issues/2783 # noqa: E501
        if not isinstance(other, type(self)):
            raise TypeError(
                "Expected an FQP object, but got object of type {}"
                .format(type(other))
            )

        for c1, c2 in zip(self.coeffs, other.coeffs):
            if c1 != c2:
                return False
        return True

    def __ne__(self: T_FQP, other: T_FQP) -> bool:     # type: ignore # https://github.com/python/mypy/issues/2783 # noqa: E501
        return not self == other

    def __neg__(self: T_FQP) -> T_FQP:
        return type(self)([-c for c in self.coeffs])

    @classmethod
    def one(cls: Type[T_FQP]) -> T_FQP:
        return cls([1] + [0] * (cls.degree - 1))

    @classmethod
    def zero(cls: Type[T_FQP]) -> T_FQP:
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
