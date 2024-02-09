def calc_diag_matrix(size):
    target = []
    for i in range(size):
        line = [(i+1)**j for j in range(size)]
        target.append(line)
    return target

# In [89]: calc_diag_matrix(2)
# Out[89]: [[1, 1], [1, 2]]

# In [90]: calc_diag_matrix(3)
# Out[90]: [[1, 1, 1], [1, 2, 4], [1, 3, 9]]