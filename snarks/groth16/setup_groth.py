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

        num_vars = int(self.circuit["nVars"])

        self.setup = {
            "vk_proof" : {
                "protocol" : "groth",
                "nVars"    : int(self.circuit["nVars"]),
                "nPublic"  : int(self.circuit["nPubInputs"] + self.circuit["nOutputs"]),
                "domainBits" : 0,
                "domainSize" : 0,
                "polsA" : [None]*num_vars,
                "polsB" : [None]*num_vars,
                "polsC" : [None]*num_vars
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
        num_constraints = len(self.circuit["constraints"])
        # consts = self.circuit["constraints"]
        for c in range(num_constraints):
            A = self.circuit["constraints"][c][0]
            B = self.circuit["constraints"][c][1]
            C = self.circuit["constraints"][c][2]
            for s in A:
                self.setup["vk_proof"]["polsA"][int(s)] = {str(c) : A[s] if A[s] != None else None}
            for s in B:
                self.setup["vk_proof"]["polsB"][int(s)] = {str(c) : B[s] if B[s] != None else None}
            for s in C:
                self.setup["vk_proof"]["polsC"][int(s)] = {str(c) : C[s] if C[s] != None else None}

        # to ensure soundness of input consistency
        # input_i * 0 = 0
        n_pub_plus_n_out = int(self.circuit["nPubInputs"]) + int(self.circuit["nOutputs"])
        for i in range(n_pub_plus_n_out+1):
            self.setup["vk_proof"]["polsA"][i] = {str(num_constraints+i) : FQ(1)}

    def calc_values_at_T(self):
        domain_bits = self.setup["vk_proof"]["domainBits"]
        toxic_t = self.setup["toxic"]["t"]
        z_t = self.PF.compute_vanishing_polynomial(domain_bits, toxic_t)
        u = self.PF.evaluate_lagrange_polynomials(domain_bits, toxic_t)

        n_vars = int(self.circuit["nVars"])

        a_t = [FQ(0)]*n_vars
        b_t = [FQ(0)]*n_vars
        c_t = [FQ(0)]*n_vars

        # print(self.setup["vk_proof"]["polsA"][0])
        # print(self.setup["vk_proof"]["polsA"][1])
        # print(self.setup["vk_proof"]["polsA"][2])

        for s in range(n_vars):
            A = self.setup["vk_proof"]["polsA"][s]
            B = self.setup["vk_proof"]["polsB"][s]
            C = self.setup["vk_proof"]["polsC"][s]
            if A != None:
                for c in A:
                    a_t[s] = a_t[s] + u[int(c)] * int(A[c])

            if B != None:
                for c in B:
                    b_t[s] = b_t[s] + u[int(c)] * int(B[c])

            if C != None:
                for c in C:
                    c_t[s] = c_t[s] + u[int(c)] * int(C[c])

        return [a_t, b_t, c_t]


    def calc_encrypted_values_at_T(self):
        num_vars = int(self.circuit["nVars"])
        n_pub_plus_n_out = int(self.circuit["nPubInputs"]) + int(self.circuit["nOutputs"]) + 1
        v = self.calc_values_at_T()
        A = [None]*num_vars
        B1 = [None]*num_vars
        B2 = [None]*num_vars
        C = [None]*num_vars
        IC = [None]*n_pub_plus_n_out

        kalfa = FQ(5) #TODO : turns into random
        kbeta = FQ(5) #TODO : turns into random
        kgamma = FQ(5) #TODO : turns into random
        kdelta = FQ(5) #TODO : turns into random

        inv_delta = 1 / kdelta
        inv_gamma = 1 / kgamma

        #TODO : alfa, beta, delta, gamma, alfa-beta paring
        #TODO : affine, paring




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
    at_list = gr.calc_values_at_T()
    # print(at_list[0])
    # print(FQ(13) * [])
