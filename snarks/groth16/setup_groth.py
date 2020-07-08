from __future__ import absolute_import
from typing import cast, List, Tuple, Sequence, Union
from field import FQ
from polfield import Polfield

IntOrFQ = Union[int, "FQ"]

class Groth:
    def __init__(self, circuit):
        self.setup = {
            "vk_proof" : {
                "protocol" : "groth",
                nVars : circuit["nVars"],
                nPublic: circuit["nPubInputs"] + circuit["nOutputs"]
            },
            "vk_verifier": {
                "protocol" : "groth",
                "nPublic" : circuit["nPubInputs"] + circuit["nOutputs"]
            },
            "toxic" : {}
        }
        total_domain = circuit["nConstraints"] + circuit["nPubInputs"] + circuit["nOutputs"]
        self.setup["vk_proof"]["domainBits"] = Polfield.log2(total_domain) + 1
        self.setup["vk_proof"]["domainSize"] = 1 << self.setup["vk_proof"]["domainBits"]

        #TODO : need random function
        self.setup["toxic"]["t"] = FQ(5)


    def calc_polynomials(self, circuit):
        return

    def calc_encrypted_value_at_T(self, circuit):
        return


# if __name__ == "__main__":
#     print("")
