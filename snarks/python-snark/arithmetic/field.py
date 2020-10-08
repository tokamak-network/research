from .field_properties import field_properties
from .field_elements import FQ
from .field2 import Field2
from .field3 import Field3
#from .field_polynomial import FieldPolynomial

class bn128_Field(FQ):
    field_modulus = field_properties["bn128"]["q"]

class bn128_Field2(Field2):
    field_modulus = field_properties["bn128"]["field_modulus"]
    nonResidue = 21888242871839275222246405745257275088696311157297823662689037894645226208582
