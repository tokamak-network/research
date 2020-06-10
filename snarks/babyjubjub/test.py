from point import Point
from field import FQ
from field import FQ2, FQ12
from field import field_properties

def encryption_test():
    # K = k*G (pubKey: K, signKey : k, generator : G)
    #
    # Encryption
    # 1. C1 = M + r*K
    # 2. C2 = r*G
    #
    # Decryption
    # 3. M = C1 - k*C2
    #
    # why?
    # -> C1 = M + r*K
    # -> M = C1 - r*K --> It fails?
    # -> M = C1 - r*k*G
    # -> M = C1 - k*C2

    G = Point.generator()

    message = 231315 # ascii 98 = b
    message_field = FQ(message)
    M = Point.from_y(message_field)

    k = 1200

    K = G * k # K = k*G, public_key
    print("Public Key : {}".format(K))

    ### Encryption Process
    ### Message(M) is encrypted with public_key(K) and random_number(r)
    ### output : C1, C2

    r = 1929319 #random number
    print("Random Number : {}".format(r))

    C1 = M + (K*r)    # C1 = M + r*K
    C2 = G * r        # C2 = r*G

    print("C1 : {}".format(C1))
    print("C2 : {}".format(C2))

    ### Decryption Process

    decrypted_M = C1 - (C2*k); # M = C1 - k*C2
    print("Decrypted Message : {}".format(decrypted_M.y))

def field_test():
    field_modulus = field_properties["bn128"]["field_modulus"]
    x = FQ2([1, 0])
    f = FQ2([1, 2])
    fpx = FQ2([2, 2])
    one = FQ2.one()
    z1, z2 = FQ2([-1, -1]).coeffs

    print("x + f == fpx                         -->", x + f == fpx)
    print("f / f == one                         -->", f / f == one)
    print("one / f + x / f == (one + x) / f     -->", one / f + x / f == (one + x) / f)
    print("one * f + x * f == (one + x) * f     -->", one * f + x * f == (one + x) * f)
    print("x ** (field_modulus ** 2 - 1) == one -->", x ** (field_modulus ** 2 - 1) == one)
    if isinstance(z1, int):
        print("z1 > 0 --> ", z1 > 0)
        print("z2 > 0 --> ", z2 > 0)
    else:
        print("z1.n > 0 -->", z1.n > 0)
        print("z2.n > 0 -->", z2.n > 0)

# encryption_test()
field_test()
