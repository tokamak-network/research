p = 71 #Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.
q = p^2-1 #Field size for program, R1CS, and QAP. 

def eval_line(g, point):
    #g(x,y)=cy+dx+e, so g == [c, d, e]
    #target line g(x,y)=g[0]y+g[1]x+g[2]
    #evaluate line at point P=(x,y)

    # out=cmod(g(1)*yp+g(2)*xp+g(3),p);

    #g(point.x, point.y)
    return g[0]*point.y + g[1]*point.x + g[2]

def ec_line(point1, point2):
    #output : g(x,y)=cy+dx+e
    #return g = [c, d, e]
    
    #TODO : make more general
    F.<z> = GF(71^2, modulus = x^2 + 1)

    #Elliptic curve: y^2=x^3+ax+b
    #in sagemath, y^2 + a1xy + a3y = x^3 +a2x^2 + a4x + a6,
    #so, a is a4, b is a6
    a = point1.curve().a4()
    b = point1.curve().a6()
    p = point1.curve().base_field().cardinality()
    k = point1.base_ring().degree() #degree

    point_inf = point1.curve().points()[1]
    point_inf_list = [point_inf[0], point_inf[1]]

    if point1.base_ring().degree() != point2.base_ring().degree():
        return
    
    if k > 1:
        P = [-point1[0], point1[1]/z]
        Q = [-point2[0], point2[1]/z]
    else:
        P = [point1[0], point1[1]]
        Q = [point2[0], point2[0]]

    xp = P[0]
    xq = Q[0]
    yp = P[1]
    yq = Q[1]

    if P == point_inf_list & Q == point_inf_list:
        #Both input points are point of infinite, not allowed
        return
    
    #TODO : make integer to integer mod
    if (xp == yp) & (xq == yq) & yp != 0:
        #tangent
        s = (3 * xp^2 + a) / (2*yp)
        c = 1
        d = -s
        e = (s * xp) - yp
    elif xp == xq:
        #vertical
        c = 0
        d = 1
        e = -xp
    elif (P == point_inf_list) & (Q != point_inf_list):
        #vertical
        c = 0
        d = 1
        e = -xq
    elif (P!= point_inf_list) & (Q == point_inf_list):
        c = 0
        d = 1
        e = -xp
    else:
        s = (yq - yp) / (xq - xp)
        c = 1
        d = -s
        e = s * xp - yp

    if k>1:
        c = c/z
        d = -d
        
    return [c, d, e]


#TODO : algo_D
#TODO : miller
#TODO : weil pairing