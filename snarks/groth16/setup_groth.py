from __future__ import absolute_import
from typing import cast, List, Tuple, Sequence, Union
from .field import FR
from .polfield import Polfield, field_modulus
from ..babyjubjub.field import FQ, FQ2
from ..babyjubjub.bn128_curve import G1, G2, mulScalar
from ..babyjubjub.bn128_paring import pairing

import json
import os

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
                #"polsA" : [None]*num_vars,
                "polsA" : [dict() for x in range(num_vars)],
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
        self.setup["toxic"]["t"] = FR(5)

        self.PF = Polfield()


    def calc_polynomials(self):
        num_constraints = len(self.circuit["constraints"])
        # consts = self.circuit["constraints"]
        for c in range(num_constraints):
            A = self.circuit["constraints"][c][0]
            B = self.circuit["constraints"][c][1]
            C = self.circuit["constraints"][c][2]
            for s in A:
                # TODO: None?
                self.setup["vk_proof"]["polsA"][int(s)] = {str(c) : A[s] if A[s] != None else None}
                #self.setup["vk_proof"]["polsA"][int(s)][c] = A[s] if A[s] != None else None
            for s in B:
                self.setup["vk_proof"]["polsB"][int(s)] = {str(c) : B[s] if B[s] != None else None}
                #self.setup["vk_proof"]["polsB"][int(s)][c] = B[s] if B[s] != None else None
            for s in C:
                self.setup["vk_proof"]["polsC"][int(s)] = {str(c) : C[s] if C[s] != None else None}
                #self.setup["vk_proof"]["polsC"][int(s)][c] = C[s] if C[s] != None else None

        # to ensure soundness of input consistency
        # input_i * 0 = 0
        n_pub_plus_n_out = int(self.circuit["nPubInputs"]) + int(self.circuit["nOutputs"])
        for i in range(n_pub_plus_n_out+1):
            self.setup["vk_proof"]["polsA"][i][num_constraints+i] = FR(1)

    def calc_values_at_T(self):
        domain_bits = self.setup["vk_proof"]["domainBits"]
        toxic_t = self.setup["toxic"]["t"]
        z_t = self.PF.compute_vanishing_polynomial(domain_bits, toxic_t)
        u = self.PF.evaluate_lagrange_polynomials(domain_bits, toxic_t)

        n_vars = int(self.circuit["nVars"])

        a_t = [FR(0)]*n_vars
        b_t = [FR(0)]*n_vars
        c_t = [FR(0)]*n_vars

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

        return [a_t, b_t, c_t, z_t]


    def calc_encrypted_values_at_T(self):
        num_vars = int(self.circuit["nVars"])
        n_pub_plus_n_out = int(self.circuit["nPubInputs"]) + int(self.circuit["nOutputs"]) + 1
        v = self.calc_values_at_T()
        A = [None]*num_vars
        B1 = [None]*num_vars
        B2 = [None]*num_vars
        C = [None]*num_vars
        IC = [None]*n_pub_plus_n_out

        kalfa = FR(5) #TODO : should turn into random
        kbeta = FR(5) #TODO : should turn into random
        kgamma = FR(5) #TODO : should turn into random
        kdelta = FR(5) #TODO : should turn into random

        inv_delta = 1 / kdelta
        inv_gamma = 1 / kgamma

        #TODO : alfa, beta, delta, gamma, alfa-beta paring
        #TODO : affine, paring

        """
        setup.vk_proof.vk_alfa_1 = G1.affine(G1.mulScalar( G1.g, setup.toxic.kalfa));
        setup.vk_proof.vk_beta_1 = G1.affine(G1.mulScalar( G1.g, setup.toxic.kbeta));
        setup.vk_proof.vk_delta_1 = G1.affine(G1.mulScalar( G1.g, setup.toxic.kdelta));

        setup.vk_proof.vk_beta_2 = G2.affine(G2.mulScalar( G2.g, setup.toxic.kbeta));
        setup.vk_proof.vk_delta_2 = G2.affine(G2.mulScalar( G2.g, setup.toxic.kdelta));


        setup.vk_verifier.vk_alfa_1 = G1.affine(G1.mulScalar( G1.g, setup.toxic.kalfa));

        setup.vk_verifier.vk_beta_2 = G2.affine(G2.mulScalar( G2.g, setup.toxic.kbeta));
        setup.vk_verifier.vk_gamma_2 = G2.affine(G2.mulScalar( G2.g, setup.toxic.kgamma));
        setup.vk_verifier.vk_delta_2 = G2.affine(G2.mulScalar( G2.g, setup.toxic.kdelta));
        """

        #print(G1, kalfa)
        vk_proof_alfa_1 = mulScalar(G1, kalfa)
        print(f"G1 : {G1}")
        print(f"kalfa : {kalfa}")
        print(f"vk_proof_alfa_1 : {vk_proof_alfa_1}")
        vk_proof_beta_1 = mulScalar(G1, kbeta)
        vk_proof_delta_1 = mulScalar(G1, kdelta)

        vk_proof_beta_2 = mulScalar(G2, kbeta)
        vk_proof_delta_2 = mulScalar(G2, kdelta)

        vk_verifier_alfa_1 = mulScalar(G1, kalfa)

        vk_verifier_beta_2 = mulScalar(G2, kbeta)
        vk_verifier_gamma_2 = mulScalar(G2, kgamma)
        vk_verifier_delta_2 = mulScalar(G2, kdelta)

        # setup.vk_verifier.vk_alfabeta_12 = bn128.pairing( setup.vk_verifier.vk_alfa_1 , setup.vk_verifier.vk_beta_2 );

        print(f"typeof vk_verifier_alfa_1 : {type(vk_verifier_alfa_1)}, {type(vk_verifier_alfa_1[0])}, {type(vk_verifier_alfa_1[1])}")
        print(f"vk_verifier_alfa_1 : {vk_verifier_alfa_1[0]}, {vk_verifier_alfa_1[1]}")
        print(f"typeof vk_verifier_beta_2 : {len(vk_verifier_beta_2)}, {type(vk_verifier_beta_2)}, {type(vk_verifier_beta_2[0])}, {type(vk_verifier_beta_2[1])}")
        print(f"vk_verifier_beta_2 : {vk_verifier_beta_2[0]}, {vk_verifier_beta_2[1]}")
        vk_verifier_alfa_1 = (FQ(12509169180663776282723030068801216576553463545861146361306867748684296333512),FQ(13767467741176394093976432344191195404568057771946939325329711084753180551863))
        vk_verifier_beta_2 = (FQ2([20954117799226682825035885491234530437475518021362091509513177301640194298072,4540444681147253467785307942530223364530218361853237193970751657229138047649]), FQ2([21508930868448350162258892668132814424284302804699005394342512102884055673846,11631839690097995216017572651900167465857396346217730511548857041925508482915]))
        vk_verifier_alfabeta_12 = pairing(vk_verifier_beta_2, vk_verifier_alfa_1)
        print(f"vk_verifier_alfabeta_12 : {vk_verifier_alfabeta_12}")


if __name__ == "__main__":

    gr = Groth(os.path.dirname(os.path.realpath(__file__)) + "/test.r1cs.json")
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
    gr.calc_encrypted_values_at_T()
    