import random
import hashlib
from Pietrzak_VDF import VDF, gen_recursive_halving_proof, verify_recursive_halving_proof, get_exp




### Unitility functions
    
def hash(*strings): # utility function for string hash
    r = hashlib.sha3_256()
    input = ''.join(map(str, strings))
    r.update(input.encode('utf-8'))
    
    return r.hexdigest()
    
def power(a,b,m):   # a^b mod m
    result = 1
    while b > 0:
        if b % 2 != 0:
            result = (result * a) % m
        b //= 2
        a = (a * a) % m

    return result
    
    
def simple_VDF(a, N, T):
    a = (a*a)%N
    for i in range(T-1):
        a = (a*a)%N
    return a
    

### Bicorn Mechanism

def GGen(N): # security parameter lambda can be omitted
    # g = random.choice(generator_list)
    # return (G, g, A, B)
    g = random.randint(2, N)
    
    return g


def construct_claim(exp_list, N, g, y, T):
    # If T is odd, make the half of T even
    if T%2 == 0:
        T_half = int(T/2)
    else:
        T_half = int((T+1)/2)   
    
    v = get_exp(exp_list, pow(2,T_half), N)    
    
    return (N, g, y, T, v)




if __name__=='__main__':
    
    
    ### Setup(l, t)
    
    # Run (G, g, A, B) <-sampling- GGen(l)
    
    a = []
    c = []    
    
    T = 10000 # VDF를 위한 파라미터. 사전 연산을 예방하며 t에 비례한 시간이 소모됨
    N = 10000000000 # 군(group)을 생성하기 위한 정수 크기 제한    

    print('\n   ___  _                       ___  _  __  ___       _____ \n \
      / _ )(_)______  _______  ____/ _ \| |/_/ / _ \___  / ___/ \n \
     / _  / / __/ _ \/ __/ _ \/___/ , _/>  <  / ___/ _ \/ /__  \n \
    /____/_/\__/\___/_/ /_//_/   /_/|_/_/|_| /_/   \___/\___/  \n')
    #print('### Bicorn-RX Proof-of-Concept ###')
    print('[+] Version 0.5\n\n')
    print('[+] PoC environment:')
    print('\t - Definition of Group: ', N)
    print('\t - Time Delay for VDF: ', T)
    print('')
    
    g = GGen(N)	
    print('g is generated as ', g)
    
    # Compute h <- g^(2^t), optionally with PoE
    #h, proof = simple_VDF(g)
    h, exp_list = VDF(N, g, T)
    print('h is generated as ', h)
    
    # Proof-of-Exponentiation proof & verification
    claim = construct_claim(exp_list, N, g, h, T)
    
    proof_list = gen_recursive_halving_proof(claim)
    print (f"\nProver sends the chain of VDF proof={proof_list}")
    
    test = verify_recursive_halving_proof(proof_list)   
    
    if (test==True):
        print("\n[+] Verifier confrimed that the prover computed correctly")
    else:
        print("\n[-] Verifier rejects the prover's VDF claim")    

    print('')
    
    # Output (G, g, h, (pi_h), A, B)
    
    ### Prepare()
    
    # a_i <-sampling- B (uniform distribution)
    member = 3  # 참여자 수
    print('[+] Number of participants: ', member, '\n')
    
    for i in range(member):
        a_i = random.randrange(0, N)
        a.append(a_i)
        print(f"a_{i} is generated as {a_i}")
    
    # c_i <- g^a_i
    for i in range(member):
        c_i = pow(g, a[i], N)    # 연산량이 크지 않으므로 ** 사용
        c.append(c_i)
        print(f"c_{i} is generated as {c_i}")
    
    ### Commit(c_i, pi_i)
    
    # Publish c_i
    
    # ----- deadline T_1 -----
    
    ### Reveal(a_i)
    
    # Publish a_i
    
    
    ### Finalize({a'_i, c_i, d_i, pi_i)}^n_i=1
    
    # b* <- H(c_1||...||c_n)
    commits = ''.join(map(str, c))
    b_star = hash(commits)
    
    # print('[+] Input commits: ', commits)
    b_star = int(b_star, 16)
    print('')
    print('[+] b*: ', hex(b_star))
    
    # For all j, Verify c_j = g^(a'_j) - else go to Recover
    # Omega = PI for i (h^H(c_i||b*))^(a'_i)
    
    print('[+] Random list: ', a)
    print('[+] Commit list: ', c)
    print('')
    
    omega = 1
    for i in range(member):
        omega = ( omega*pow(pow(h, int(hash(c[i], b_star), 16), N), a[i], N) ) % N
        
    print('[+] Optimistically constructed random is: ', omega, '\n')
    
    ##### recovery scenario #####
    
    omega = 1
    for i in range(member-1):
        omega = (omega * pow( pow(h, int(hash(c[i], b_star), 16), N), a[i], N) ) % N
    
    # Suppose a_2 is not submitted
    # Omega = [PI for i c_i^H(c_i||b*) ]^(2^t)
    
    recovery_index = [2]
    print('[+] Suppose lost indices: ', recovery_index)
    print('\n------------------------------------------------\n')
    print('Recovery------>')
    print('\n------------------------------------------------\n')

    
    recov = 1
    
    for i in recovery_index:
        temp = pow(c[i], int(hash(c[i], b_star), 16), N)
        recov = (recov * temp) % N
       
    recov_backup = recov 
    recov = simple_VDF(recov, N, T)
    
    h_recov, exp_list_recov = VDF(N, recov_backup, T)
    print('h is generated as ', h)
    
    # Proof-of-Exponentiation proof & verification
    claim = construct_claim(exp_list_recov, N, recov_backup, h_recov, T)
    
    proof_list = gen_recursive_halving_proof(claim)
    print (f"\nProver computes and sends the chain of VDF proof={proof_list}")
    
    test = verify_recursive_halving_proof(proof_list)   
    
    if (test==True):
        print("\n[+] Verifier confrimed that the prover computed correctly")
    else:
        print("\n[-] Verifier rejects the prover's VDF claim")    

    print('')    
        
    omega = omega * recov % N
        
    print('[+] Pessimistically constructed random is: ', omega)
