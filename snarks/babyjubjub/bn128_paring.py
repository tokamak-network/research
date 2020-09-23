# https://github.com/ethereum/py_ecc
# 현재 7월 2일까지 총 세개의 파워포인트를 작성하였습니다. 5월 22일 발표자료, 6월 12일 발표자료, 6월 26일 발표자료를 각각 발표자료 1, 2, 3이라 칭하겠습니다.
 
# FQ, FQ2, FQ12는 각각 prime field, twisted field, extended field에서 정의된 숫자를 표현하기위한 자료형입니다.
# FQ는 prime field를 표현하며, FQ자료형의 값은 prime number q보다 작고 0보다 큰 정수입니다.
# FQ12는 FQ를 embedding degree 12로 확장한 extension field를 표현합니다. FQ12 자료형의 값은 길이 12의 배열이고, 모든 원소는 0보다 크고 q보다 작은 정수입니다. 예를 들어 FQ3이라면, 3+1*root(2)+2*root(-1) 이라는 값을 [3,1,2]로 저장하는 것입니다. 여기서 root(2)와 root(-1)은 예를 들기위해 임의로 설정한 값으로, extension을 어떻게 하느냐에 따라 달라지는 숫자입니다. [발표자료 3의 24슬라이드에 FQ->FQ2의 field extension의 예시가 있음]
# FQ2는 FQ12에서 정의된 좌표들을 degree 6으로 twist한 후 생겨나는 twisted 좌표를 정의할 quadratic field를 표현합니다. FQ2 자료형의 값은 길이 2의 배열이고, 모든 원소는 0보다 크고 q보다 작은 정수입니다. [발표자료 3의 31슬라이드에 FQ2->FQ의 twisting의 예시가 있음]
# FQP는 FQ와 같은 prime field이지만, polynomial 연산을 구현하기위해 FQ와 구분해놓은것입니다. pairing에서는 사용되지 않습니다.
from .field import FQ, FQP, FQ2, FQ12, field_properties

from typing import (
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from .bn128_curve import (
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


# Point2D는 EC의 좌표를 affine coordinate로 표현하는 자료형입니다. 우리에게 익숙한 그 좌표계입니다.
Point2D = Optional[Tuple[Field, Field]]  # Point at infinity is encoded as a None
# Point3D는 EC의 좌표를 projective coordinate로 표현하는 자료형입니다. 사용하지 않습니다. [정순형 대표님이 공유하신 부산대 발표자료의 17슬라이드]
# 하나의 커브 좌표가 주어졌을때, 그 좌표를 affine coordinate <-> projective coordinate로 one-to-one mapping 할 수 있습니다. 이 코드도 그렇고, 제가 본 문헌들에서도 affine 좌표만을 사용하지, projective 좌표로 변환시켜 사용하는것은 아직 못봤습니다. 얼핀 찾아보기엔 projective 좌표계를 사용하면 커브 포인트 연산을 할 때 소요되는 계산량이 더 큽니다. 아직 projective 좌표계를 사용할때의 이점이 뭔지는 잘 모르겠네요. 
Point3D = Optional[Tuple[Field, Field, Field]]  # Point at infinity is encoded as a None
GeneralPoint = Union[Point2D[Field], Point3D[Field]]

ate_loop_count = 29793968203157093288
log_ate_loop_count = 63

# Create a function representing the line between P1 and P2,
# and evaluate it at T
# 예를 들어 P1과 P2를 지나는 직선의 방정식이 d:y+cx+d=0이고, T=(2,1)이라면, linefunc의 결과 값은 (1+2*c+d)가 됩니다.
# 발표자료2의 29슬라이드를 보면, pairing은 f_P와 f_Q라는 함수를 만들고 그 함수의 입력으로 각각 A_Q와 A_P를 넣습니다.
# 여기서 f_P(A_Q)에 집중하여 설명드리겠습니다.
# A_Q는 divisor입니다. divisor란 좌표들을 저장하는 저장수단입니다. [발표자료2의 슬라이드16]
# Weil pairing에서 A_Q=(Q-R)-(R)로 정의되어 있습니다. 그 말은 A_Q에는 두 개의 좌표가 저장되어 있는데, 하나는 (Q-R)이고, 다른 하나는 (R)입니다. [발표자료2의 슬라이드19]
# f_P는 분자와 분모가 x,y의 polynomial인 함수입니다. f_P는 많은 직선의 방정식들을 서로 곱하고 나눔으로써 만들어집니다. [발표자료2의 21-28 슬라이드]
# f_p를 구성하는 직선의 방정식을 찾기위해 사용되는 함수가 linefunc 함수입니다.
# 만약 f_P를 건설 완료했다면, f_P(A_Q)=f_P((Q-R)-(R)):=f_P(Q-R)/f_P(R)로 계산 할 수 있습니다. [발표자료2의 슬라이드20 우측하단]
# 예를 들어, f_P의 건설에 직선의 방정식 l(x,y), m(x,y), d(x,y)이 사용되고 f_P=l*m/d 이라면, f_P(A_Q)=(l(Q-R)*m(Q-R)/d(Q-R)) / (l(R)*m(R)/d(R))로 계산 할 수 있습니다.
# 이때 linefunc 함수가 모든 요소들인 l(Q-R),m(Q-R),d(Q-R),l(R),m(R),d(R) 을 계산해줍니다 (linefunc의 입력 T에 Q-R 과 R이 들어갑니다).
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
        # 직선의 방정식은 d(x,y)=y-m*(x-x1)-y1 입니다.
        m = 3 * x1**2 / (2 * y1)
        # 직선의 방정식 d에 x=xt, y=yt를 대입하여 결과를 return합니다. 
        return m * (xt - x1) - (yt - y1)
    else:
        return xt - x1

# FQ자료형을 FQ12자료형으로 변환합니다. 값에는 변화가 없고, 뒤에 zero를 padding하여 정수를 길이 12의 배열로 바꿔줍니다.
def cast_point_to_fq12(pt: Point2D[FQ]) -> Point2D[FQ12]:
    if pt is None:
        return None
    x, y = pt
    fq12_point = (FQ12([x.n] + [0] * 11), FQ12([y.n] + [0] * 11))
    return fq12_point


# Check consistency of the "line function"
# debugging용 코드입니다.
one, two, three = G1, double(G1), multiply(G1, 3)
# negone과 negtwo, negthree는 각각 one과 two, three의 inverse입니다. 왜냐하면 G1이 generator인데, 그 말은 G1*curve_order=(Point at infinity)이고, 따라서 one+negone=(Point at infinity)가 되기 때문입니다.
negone, negtwo, negthree = (
    multiply(G1, curve_order - 1),
    multiply(G1, curve_order - 2),
    multiply(G1, curve_order - 3),
)

# 예를들어 어떤 직선 d가 두 점 one과 two를 지난다고 하면, d(one)=d(two)=0 입니다. 이를 만족하는지 체크합니다.
assert linefunc(one, two, one) == FQ(0)
assert linefunc(one, two, two) == FQ(0)
# 그런데 어떤 두 점 one과 two를 지나는 직선 d는 반드시 다른 하나의 점을 더 지납니다. Elliptic curve가 그렇게 설계뙨 curve입니다.
# 그 다른 하나의 점은 -(one+two), 즉 negthree입니다.
# 따라서 직선 d는 반드시 d(one)=d(two)=d(negthree)=0을 만족해야 합니다.
# 한편 직선 d는 three라는 점은 지나지 않기 때문에, d(three)!=0을 만족해야 합니다.
assert linefunc(one, two, three) != FQ(0)
assert linefunc(one, two, negthree) == FQ(0)
# 아래도 마찬가지입니다.
assert linefunc(one, negone, one) == FQ(0)
assert linefunc(one, negone, negone) == FQ(0)
assert linefunc(one, negone, two) != FQ(0)
assert linefunc(one, one, one) == FQ(0)
assert linefunc(one, one, two) != FQ(0)
assert linefunc(one, one, negtwo) == FQ(0)


# Main miller loop
# https://crypto.stanford.edu/~dabo/papers/bfibe.pdf 의 appendix에 정리되어있는 pseudo code를 구현한 코드입니다.
# 제가 MATLAB으로 구현한 miller loop도 마찬가지로 위의 pseudo code를 구현한것입니다.
# 제 발표자료3의 슬라이드 15-18이 miller loop을 설명하고 있긴 하지만, 위의 appendix에 적혀있는 설명이 훨씬 더 간결하고 친절하고, 명확합니다.
# 요청하시면 구두로 몇 번이든 다시 설명드릴 수 있지만, 제 설명은 보조적인 역할만 할 뿐, 위의 appendix를 시간내어 공부해보시는것을 추천드립니다. 그게 가장 빠를겁니다.

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
    print("#"*80, "pairing begin")
    print(f"P : {P}")
    print(f"Q : {Q}")
    print(f"twist(Q) : {twist(Q)}")
    print(f"cast_point_to_fq12(P) : {cast_point_to_fq12(P)}")
    print("#"*80, "pairing end")
    #return miller_loop(twist(Q), cast_point_to_fq12(P))
    return miller_loop(Q, cast_point_to_fq12(P))


def final_exponentiate(p: Field) -> Field:
    return p ** ((field_modulus ** 12 - 1) // curve_order)
