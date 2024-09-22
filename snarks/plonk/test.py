from utils import Setup
import prover as p
import verifier as v
import compiler as c

from compiler import to_assembly


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

    #to_assemply(eqs)
    # [(['e', None, None], {'e': -1, '$output_coeff': 0, '$public': True}),
    # (['a', 'b', 'c'], {'a*b': 1}),
    # (['c', 'd', 'e'], {'c*d': 1})]

    ##VERIFY
    v.verify_proof(setup, 8, vk, proof, public, optimized=False)
    v.verify_proof(setup, 8, vk, proof, public, optimized=True)

def test2():
    ##SETUP##
    setup = Setup.from_file("./powersOfTau28_hez_final_11.ptau")
    
    ##PROOF##
    eqs = """
        n public
        pb0 === pb0 * pb0
        pb1 === pb1 * pb1
        pb2 === pb2 * pb2
        pb3 === pb3 * pb3
        qb0 === qb0 * qb0
        qb1 === qb1 * qb1
        qb2 === qb2 * qb2
        qb3 === qb3 * qb3
        pb01 <== pb0 + 2 * pb1
        pb012 <== pb01 + 4 * pb2
        p <== pb012 + 8 * pb3
        qb01 <== qb0 + 2 * qb1
        qb012 <== qb01 + 4 * qb2
        q <== qb012 + 8 * qb3
        n <== p * q
    """

    # to_assemply(eqs) ->
    # [(['n', None, None], {'n': -1, '$output_coeff': 0, '$public': True}),
    # (['pb0', 'pb0', 'pb0'], {'pb0*pb0': 1}),
    # (['pb1', 'pb1', 'pb1'], {'pb1*pb1': 1}),
    # (['pb2', 'pb2', 'pb2'], {'pb2*pb2': 1}),
    # (['pb3', 'pb3', 'pb3'], {'pb3*pb3': 1}),
    # (['qb0', 'qb0', 'qb0'], {'qb0*qb0': 1}),
    # (['qb1', 'qb1', 'qb1'], {'qb1*qb1': 1}),
    # (['qb2', 'qb2', 'qb2'], {'qb2*qb2': 1}),
    # (['qb3', 'qb3', 'qb3'], {'qb3*qb3': 1}),
    # (['pb0', 'pb1', 'pb01'], {'pb1': 2, 'pb0': 1}),
    # (['pb01', 'pb2', 'pb012'], {'pb01': 1, 'pb2': 4}),
    # (['pb012', 'pb3', 'p'], {'pb012': 1, 'pb3': 8}),
    # (['qb0', 'qb1', 'qb01'], {'qb1': 2, 'qb0': 1}),
    # (['qb01', 'qb2', 'qb012'], {'qb01': 1, 'qb2': 4}),
    # (['qb012', 'qb3', 'q'], {'qb3': 8, 'qb012': 1}),
    # (['p', 'q', 'n'], {'p*q': 1})]
    public = [91]
    assignments = c.fill_variable_assignments(eqs, {
        'pb3': 1, 'pb2': 1, 'pb1': 0, 'pb0': 1,
        'qb3': 0, 'qb2': 1, 'qb1': 1, 'qb0': 1,
    })
    proof = p.prove_from_witness(setup, 16, eqs, assignments)

    ##VERIFICATION KEY##
    vk = c.make_verification_key(setup, 16, eqs)

    ##VERIFY
    v.verify_proof(setup, 16, vk, proof, public, optimized=False)
    v.verify_proof(setup, 16, vk, proof, public, optimized=True)   


def test_flatcode_to_eqs():
    flat = [['*', 'sym_1', 'x', 'x'], ['*', 'y', 'sym_1', 'x'], ['+', 'sym_2', 'y', 'x'], ['+', '~out', 'sym2', 5]]
    eqs_before = ["out public"]
    for line in flat:
        expr = str(line[1]) + " <== " + str(line[2]) + " " + str(line[0]) + " " + str(line[3])
        eqs_before.append(expr)

    eqs = [line.strip("~").replace("_","") for line in eqs_before]
    print(eqs)

    #eqs = 
    # [
    #   'out public', 
    #   'sym1 <== x * x', 
    #   'y <== sym1 * x', 
    #   'sym2 <== y + x', 
    #   'out <== sym2 + 5'
    # ]

    ##SETUP##
    setup = Setup.from_file("./powersOfTau28_hez_final_11.ptau")

    public = [35]
    assignments = {'x': 3, 'sym1': 9, 'y': 27, 'sym2': 30, 'out': 35}

    proof = p.prove_from_witness(setup, 8, eqs, assignments)

    ##VERIFICATION KEY##
    vk = c.make_verification_key(setup, 8, eqs)

    ##VERIFY
    v.verify_proof(setup, 8, vk, proof, public, optimized=False)
    v.verify_proof(setup, 8, vk, proof, public, optimized=True)

def test_compiler_to_assemply():
    setup = Setup.from_file("./powersOfTau28_hez_final_11.ptau")
    eqs1 = ['e public', 'c <== a * b', 'e <== c * d']
    eqs2 = """
        n public
        pb0 === pb0 * pb0
        pb1 === pb1 * pb1
        pb2 === pb2 * pb2
        pb3 === pb3 * pb3
        qb0 === qb0 * qb0
        qb1 === qb1 * qb1
        qb2 === qb2 * qb2
        qb3 === qb3 * qb3
        pb01 <== pb0 + 2 * pb1
        pb012 <== pb01 + 4 * pb2
        p <== pb012 + 8 * pb3
        qb01 <== qb0 + 2 * qb1
        qb012 <== qb01 + 4 * qb2
        q <== qb012 + 8 * qb3
        n <== p * q
    """
    o = to_assembly(eqs1)
    print("input : {}".format(eqs1))
    print("output : {}".format(o))

# test()
# test2()
# test_compiler_to_assemply()
test_flatcode_to_eqs()

