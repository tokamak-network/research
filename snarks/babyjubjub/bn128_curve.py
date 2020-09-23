# https://github.com/ethereum/py_ecc

from .field import FQ, FQP, FQ2, FQ12, field_properties

from typing import (
    Optional,
    Tuple,
    TypeVar,
    Union,
)

field_modulus = field_properties["bn128"]["field_modulus"]
curve_order = 21888242871839275222246405745257275088548364400416034343698204186575808495617

Field = TypeVar(
    'Field',
    # General
    FQ,
    FQP,
    FQ2,
    FQ12,
)

Point2D = Optional[Tuple[Field, Field]]  # Point at infinity is encoded as a None
Point3D = Optional[Tuple[Field, Field, Field]]  # Point at infinity is encoded as a None
GeneralPoint = Union[Point2D[Field], Point3D[Field]]

# Curve order should be prime
assert pow(2, curve_order, curve_order) == 2
# Curve order should be a factor of field_modulus**12 - 1
assert (field_modulus ** 12 - 1) % curve_order == 0

# Curve is y**2 = x**3 + 3
b = FQ(3)
# Twisted curve over FQ**2
b2 = FQ2([3, 0]) / FQ2([9, 1])
# Extension curve over FQ**12; same b value as over FQ
b12 = FQ12([3] + [0] * 11)

# Generator for curve over FQ
G1 = (FQ(1), FQ(2))
# Generator for twisted curve over FQ2
G2 = (
    FQ2([
        10857046999023057135944570762232829481370756359578518086990519993285655852781,
        11559732032986387107991004021392285783925812861821192530917403151452391805634,
    ]),
    FQ2([
        8495653923123431417604973247489272438418190587263600148770280649306958101930,
        4082367875863433681332203403145435568316851327593401208105741076214120093531,
    ]),
)
# Point at infinity over FQ
Z1 = None
# Point at infinity for twisted curve over FQ2
Z2 = None

# Check if a point is the point at infinity
def is_inf(pt: GeneralPoint[Field]) -> bool:
    return pt is None


# Check that a point is on the curve defined by y**2 == x**3 + b
def is_on_curve(pt: Point2D[Field], b: Field) -> bool:
    if is_inf(pt):
        return True
    x, y = pt
    return y**2 - x**3 == b


assert is_on_curve(G1, b)
assert is_on_curve(G2, b2)


# Elliptic curve doubling
def double(pt: Point2D[Field]) -> Point2D[Field]:
    if is_inf(pt):
        return pt
    x, y = pt
    m = 3 * x**2 / (2 * y)
    newx = m**2 - 2 * x
    newy = -m * newx + m * x - y
    return (newx, newy)


# Elliptic curve addition
# https://en.wikipedia.org/wiki/Elliptic_curve#The_group_law
def add(p1: Point2D[Field],
        p2: Point2D[Field]) -> Point2D[Field]:
    if p1 is None or p2 is None:
        return p1 if p2 is None else p2
    x1, y1 = p1
    x2, y2 = p2
    if x2 == x1 and y2 == y1:
        return double(p1)
    elif x2 == x1:
        return None
    else:
        m = (y2 - y1) / (x2 - x1)
    newx = m**2 - x1 - x2
    newy = -m * newx + m * x1 - y1
    assert newy == (-m * newx + m * x2 - y2)
    return (newx, newy)


# Elliptic curve point multiplication
def multiply(pt: Point2D[Field], n: int) -> Point2D[Field]:
    if n == 0:
        return None
    elif n == 1:
        return pt
    elif not n % 2:
        return multiply(double(pt), n // 2)
    else:
        return add(multiply(double(pt), int(n // 2)), pt)

"""
module.exports.naf = function naf(n) {
    let E = BigInt(n);
    const res = [];
    while (E) {
        if (E & 1n) {
            const z = 2 - Number(E % 4n);
            res.push( z );
            E = E - BigInt(z);
        } else {
            res.push( 0 );
        }
        E = E >> 1n;
    }
    return res;
};
"""

def naf(n):
    res = []
    nn = int(n)
    while nn:
        if nn & 1:
            z = 2 - (nn % 4)
            res.append(z)
            nn = nn - z
        else:
            res.append(0)
        nn = nn >> 1
    return res

"""
exports.mulScalar = (F, base, e) => {
    let res;

    if (Scalar.isZero(e)) return F.zero;

    const n = Scalar.naf(e);

    if (n[n.length-1] == 1) {
        res = base;
    } else if (n[n.length-1] == -1) {
        res = F.neg(base);
    } else {
        assert(false);
    }

    for (let i=n.length-2; i>=0; i--) {

        res = F.double(res);

        if (n[i] == 1) {
            res = F.add(res, base);
        } else if (n[i] == -1) {
            res = F.sub(res, base);
        }
    }

    return res;
};
"""

def mulScalar(base, e):
    if e == 0:
        return 0
    n = naf(e)
    res = None
    if n[len(n) - 1] == 1:
        res = base
    elif n[len(n) - 1] == -1:
        res = neg(base)
    else:
        raise ValueError("mulScalar invalid value")

    for i in range(len(n) - 2, 0, -1):
        res = double(res)
        if n[i] == 1:
            res = add(res, base)
        elif n[i] == -1:
            res = add(res, neg(base))
    return res

def eq(p1: GeneralPoint[Field], p2: GeneralPoint[Field]) -> bool:
    return p1 == p2


# "Twist" a point in E(FQ2) into a point in E(FQ12)
w = FQ12([0, 1] + [0] * 10)


# Convert P => -P
def neg(pt: Point2D[Field]) -> Point2D[Field]:
    if pt is None:
        return None
    x, y = pt
    return (x, -y)


def twist(pt: Point2D[FQP]) -> Point2D[FQ12]:
    if pt is None:
        return None
    _x, _y = pt
    # Field isomorphism from Z[p] / x**2 to Z[p] / x**2 - 18*x + 82
    xcoeffs = [_x.coeffs[0] - _x.coeffs[1] * 9, _x.coeffs[1]]
    ycoeffs = [_y.coeffs[0] - _y.coeffs[1] * 9, _y.coeffs[1]]
    # Isomorphism into subfield of Z[p] / w**12 - 18 * w**6 + 82,
    # where w**6 = x
    nx = FQ12([int(xcoeffs[0])] + [0] * 5 + [int(xcoeffs[1])] + [0] * 5)
    ny = FQ12([int(ycoeffs[0])] + [0] * 5 + [int(ycoeffs[1])] + [0] * 5)
    # Divide x coord by w**2 and y coord by w**3
    return (nx * w ** 2, ny * w**3)


G12 = twist(G2)
# Check that the twist creates a point that is on the curve
assert is_on_curve(G12, b12)
