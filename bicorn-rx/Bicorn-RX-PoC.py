import random
import hashlib

### Setup(l, t)

# Run (G, g, A, B) <-sampling- GGen(l)
time = 10000000 # VDF를 위한 파라미터. 사전 연산을 예방하며 t에 비례한 시간이 소모됨
order = 277 # 군(group)을 생성하기 위한 정수 크기 제한
generator_list = [5, 6, 11, 14, 17, 18, 20, 24, 31, 43, 44, 45, 46, 50, 53, 56, 58, 65, 68, 72, 77, 78, 80, 93, 94, 96, 97, 98, 99, 101, 103, 105, 107, 110, 111, 114, 115, 119, 124, 126, 127, 134, 135, 137, 140, 142, 143, 150, 151, 153, 158, 162, 163, 166, 167, 170, 172, 174, 176, 178, 179, 180, 181, 183, 184, 197, 199, 200, 205, 209, 212, 219, 221, 224, 227, 231, 232, 233, 234, 246, 253, 257, 259, 260, 263, 266, 271, 272] # 사전에 생성된 order 에 대한 generator 리스트 -> 효율적
a = []
c = []


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
    
def power_mod_order(a,b):
    return power(a,b, order)
    
def simple_VDF(a):
    a = (a*a)%order
    for i in range(time-1):
        a = (a*a)%order
    return a
    
### Bicorn Mechanism

def GGen(): # security parameter lambda can be omitted
    g = random.choice(generator_list)
    #return (G, g, A, B)
    return g

print('\n   ___  _                       ___  _  __  ___       _____ \n \
  / _ )(_)______  _______  ____/ _ \| |/_/ / _ \___  / ___/ \n \
 / _  / / __/ _ \/ __/ _ \/___/ , _/>  <  / ___/ _ \/ /__  \n \
/____/_/\__/\___/_/ /_//_/   /_/|_/_/|_| /_/   \___/\___/  \n')
#print('### Bicorn-RX Proof-of-Concept ###')
print('[+] PoC environment:')
print('\t - Order of Group: ', order)
print('\t - Time Delay for VDF: ', time)
print('')

g = GGen()	
print('g is generated as ', g)

# Compute h <- g^(2^t), optionally with PoE
h = simple_VDF(g)
print('h is generated as ', h)
print('')

# Output (G, g, h, (pi_h), A, B)

### Prepare()

# a_i <-sampling- B (uniform distribution)
member = 3  # 참여자 수
print('[+] Number of participants: ', member, '\n')

for i in range(member):
    a_i = random.randrange(0, order)
    a.append(a_i)
    print(f"a_{i} is generated as {a_i}")

# c_i <- g^a_i
for i in range(member):
    c_i = power_mod_order(g,a[i])    # 연산량이 크지 않으므로 ** 사용
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
    omega = ( omega*power_mod_order(power_mod_order(h, int(hash(c[i], b_star), 16)), a[i]) ) % order
    
print('[+] Optimistically constructed random is: ', omega, '\n')

##### recovery scenario #####

omega = 1
for i in range(member-1):
    omega = ( omega*power_mod_order(power_mod_order(h,int(hash(c[i], b_star), 16)), a[i]) ) % order

# Suppose a_2 is not submitted
# Omega = [PI for i c_i^H(c_i||b*) ]^(2^t)

recovery_index = [2]
print('[+] Suppose lost indices: ', recovery_index)
print('Recovery------>')

recov = 1
for i in recovery_index:
    temp = power_mod_order(c[i], int(hash(c[i], b_star), 16))
    recov = (recov * temp) % order
recov = simple_VDF(recov)
    
omega = omega * recov % order
    
print('[+] Pessimistically constructed random is: ', omega)
