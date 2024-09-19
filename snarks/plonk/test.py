from utils import Setup
import prover as p
import verifier as v
import compiler as c


def test():
    ##SETUP##
    setup = Setup.from_file("./powersOfTau28_hez_final_11.ptau")
    
    ##PROOF##
    eqs = ['e public', 'c <== a * b', 'e <== c * d']
    public = [60]
    assignments = {'a': 3, 'b': 4, 'c': 12, 'd': 5, 'e': 60}
    proof = p.prove_from_witness(setup, 8, eqs, assignments)

    ##VERIFICATION KEY##
    vk = c.make_verification_key(setup, 8, eqs)

    ##VERIFY
    v.verify_proof(setup, 8, vk, proof, public, optimized=False)
    v.verify_proof(setup, 8, vk, proof, public, optimized=True)

test()