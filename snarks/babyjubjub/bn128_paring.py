# https://github.com/ethereum/py_ecc
# 현재 7월 2일까지 총 세개의 파워포인트를 작성하였습니다. 5월 22일 발표자료, 6월 12일 발표자료, 6월 26일 발표자료를 각각 발표자료 1, 2, 3이라 칭하겠습니다.
 
# FQ, FQ2, FQ12는 각각 prime field, twisted field, extended field에서 정의된 Elliptic Curve(EC)의 좌표를 표현하기위한 자료형입니다.
# FQ는 prime field를 표현하며, (x,y)의 형태로 정의됩니다. 여기서 x와 y는 prime number q보다 작고 0보다 큰 정수입니다.
# FQ12는 FQ를 embedding degree 12로 확장한 extension field를 표현하며, (X,Y)의 형태로 정의됩니다. 여기서 X와 Y는 각각 길이 12의 배열이고, 배열의 모든 원소는 0보다 크고 q보다 작은 정수입니다. [발표자료 3의 24슬라이드에 FQ->FQ2의 field extension의 예시가 있음]
# FQ2는 FQ12에서 정의된 좌표들을 degree 6으로 twist한 후 생겨나는 twisted 좌표를 정의할 quadratic field를 표현하며, (A,B)의 형태로 정의됩니다. 여기서 A와 B는 각각 길이 2의 배열이고, 배열의 모든 원소는 0보다 크고 q보다 작은 정수입니다. [발표자료 3의 31슬라이드에 FQ2->FQ의 twisting의 예시가 있음]
# FQP는 FQ와 같은 prime field이지만, polynomial 연산을 구현하기위해 FQ와 구분해놓은것입니다. pairing에서는 사용되지 않습니다.
from field import FQ, FQP, FQ2, FQ12, field_properties

from typing import (
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from bn128_curve import (
    double,
    add,
    multiply,
    is_on_curve,
    twist,
    b,
    b2,
    curve_order,
    # G1은 elliptic curve의 모든 좌표들이 원소인 "커브 그룹"의 generator입니다. generator를 n번 multiply 함으로써 모든 원소를 다 만들어낼 수 있습니다 (1<=n<=r, 여기서 r은 group order).
    G1,
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

ate_loop_count = 29793968203157093288
log_ate_loop_count = 63

# Create a function representing the line between P1 and P2,
# and evaluate it at T
def linefunc(P1: Point2D[Field],
             P2: Point2D[Field],
             T: Point2D[Field]) -> Field:
    assert P1 and P2 and T  # No points-at-infinity allowed, sorry
    x1, y1 = P1
    x2, y2 = P2
    xt, yt = T
    if x1 != x2:
        m = (y2 - y1) / (x2 - x1)
        return m * (xt - x1) - (yt - y1)
    elif y1 == y2:
        m = 3 * x1**2 / (2 * y1)
        return m * (xt - x1) - (yt - y1)
    else:
        return xt - x1


def cast_point_to_fq12(pt: Point2D[FQ]) -> Point2D[FQ12]:
    if pt is None:
        return None
    x, y = pt
    fq12_point = (FQ12([x.n] + [0] * 11), FQ12([y.n] + [0] * 11))
    return fq12_point


# Check consistency of the "line function"
one, two, three = G1, double(G1), multiply(G1, 3)
negone, negtwo, negthree = (
    multiply(G1, curve_order - 1),
    multiply(G1, curve_order - 2),
    multiply(G1, curve_order - 3),
)


assert linefunc(one, two, one) == FQ(0)
assert linefunc(one, two, two) == FQ(0)
assert linefunc(one, two, three) != FQ(0)
assert linefunc(one, two, negthree) == FQ(0)
assert linefunc(one, negone, one) == FQ(0)
assert linefunc(one, negone, negone) == FQ(0)
assert linefunc(one, negone, two) != FQ(0)
assert linefunc(one, one, one) == FQ(0)
assert linefunc(one, one, two) != FQ(0)
assert linefunc(one, one, negtwo) == FQ(0)


# Main miller loop
def miller_loop(Q: Point2D[FQ12],
                P: Point2D[FQ12]) -> FQ12:
    if Q is None or P is None:
        return FQ12.one()
    R = Q   # type: Point2D[FQ12]
    f = FQ12.one()
    for i in range(log_ate_loop_count, -1, -1):
        f = f * f * linefunc(R, R, P)
        R = double(R)
        if ate_loop_count & (2**i):
            f = f * linefunc(R, Q, P)
            R = add(R, Q)
    # assert R == multiply(Q, ate_loop_count)
    Q1 = (Q[0] ** field_modulus, Q[1] ** field_modulus)
    # assert is_on_curve(Q1, b12)
    nQ2 = (Q1[0] ** field_modulus, -Q1[1] ** field_modulus)
    # assert is_on_curve(nQ2, b12)
    f = f * linefunc(R, Q1, P)
    R = add(R, Q1)
    f = f * linefunc(R, nQ2, P)
    # R = add(R, nQ2) This line is in many specifications but it technically does nothing
    return f ** ((field_modulus ** 12 - 1) // curve_order)


# Pairing computation
def pairing(Q: Point2D[FQ2], P: Point2D[FQ]) -> FQ12:
    assert is_on_curve(Q, b2)
    assert is_on_curve(P, b)
    return miller_loop(twist(Q), cast_point_to_fq12(P))


def final_exponentiate(p: Field) -> Field:
    return p ** ((field_modulus ** 12 - 1) // curve_order)
