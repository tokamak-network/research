def generators(n):
    s = set(range(1, n))
    results = []
    for a in s:
        g = set()
        for x in s:
            g.add((a**x) % n)
        if g == s:
            results.append(a)
    return results

def print_till():
    for i in range(1000):
        gens = generators(i)
        if gens:
            print(f"Z_{i} has generators {gens}")

#print_till()
order = 277 # order should be a prime number to have generators
gens = generators(order)
if gens:
    print(f"Z_{order} has generators {gens}")
    


