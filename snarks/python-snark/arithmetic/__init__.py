"""
from .field import bn128_Field, bn128_FieldPolynomial
from .utils import log2
"""


from .field_properties import field_properties
from .field_elements import FQ
from .field_polynomial import bn128_FieldPolynomial
from .utils import log2, mul_scalar
from .bn128 import G1, G2, pairing

class bn128_Field(FQ):
    field_modulus = field_properties["bn128"]["q"]
