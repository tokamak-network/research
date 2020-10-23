from .field_properties import field_properties
from .field_elements import FQ
from .utils import log2, mul_scalar
from .bn128 import G1, G2, pairing, bn128_FieldPolynomial, CurvePoint, PolField, F1_P, F12

class bn128_Field(FQ):
    field_modulus = field_properties["bn128"]["q"]
