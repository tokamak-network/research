from __future__ import absolute_import
from typing import cast, List, Tuple, Sequence, Union
from field import FQ
from polfield import Polfield, field_modulus

import json

IntOrFQ = Union[int, "FQ"]

class Groth:
    def __init__(self, circuit_path):

        with open(circuit_path) as json_file:
            self.circuit = json.load(json_file)

        self.setup = {
            "vk_proof" : {
                "protocol" : "groth",
                "nVars"    : int(self.circuit["nVars"]),
                "nPublic"  : int(self.circuit["nPubInputs"] + self.circuit["nOutputs"]),
                "domainBits" : 0,
                "domainSize" : 0,
                "polsA" : {},
                "polsB" : {},
                "polsC" : {}
            },
            "vk_verifier": {
                "protocol" : "groth",
                "nPublic"  : int(self.circuit["nPubInputs"] + self.circuit["nOutputs"])
            },
            "toxic" : {}
        }
        total_domain = int(self.circuit["nConstraints"]) + int(self.circuit["nPubInputs"]) + int(self.circuit["nOutputs"])
        self.setup["vk_proof"]["domainBits"] = Polfield.log2(total_domain) + 1
        self.setup["vk_proof"]["domainSize"] = 1 << self.setup["vk_proof"]["domainBits"]

        #TODO : need random function
        self.setup["toxic"]["t"] = FQ(5)

        self.PF = Polfield()


    def calc_polynomials(self):
        # TODO : check if length affect the result
        for c in self.circuit["constraints"]:
            self.setup["vk_proof"]["polsA"].update(c[0])
            self.setup["vk_proof"]["polsB"].update(c[1])
            self.setup["vk_proof"]["polsC"].update(c[2])

    def calc_values_at_T(self):
        domain_bits = self.setup["vk_proof"]["domainBits"]
        toxic_t = self.setup["toxic"]["t"]
        z_t = self.PF.compute_vanishing_polynomial(domain_bits, toxic_t)
        u = self.PF.evaluate_lagrange_polynomials(domain_bits, toxic_t)
        # print(domain_bits)
        # print(toxic_t)
        # print(z_t)
        # print(u)

        n_vars = int(self.circuit["nVars"])

        a_t = [FQ(0)]*n_vars
        b_t = [FQ(0)]*n_vars
        c_t = [FQ(0)]*n_vars

        print(a_t)
        print(len(a_t))


    # def calc_encrypted_value_at_T(self, circuit):
    #     return


if __name__ == "__main__":

    gr = Groth("test.r1cs.json")
    # print(gr.setup)
    gr.calc_polynomials()
    # polsA = gr.setup["vk_proof"]["polsA"]
    # polsB = gr.setup["vk_proof"]["polsB"]
    # polsC = gr.setup["vk_proof"]["polsC"]
    # print(polsA)
    # print(len(polsA))
    # print(len(polsB))
    # print(len(polsC))
    gr.calc_values_at_T()
    # print(FQ(13) * [])
