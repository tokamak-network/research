function [ modified_Point ] = EC_order( Point )
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here
modified_Point=Point;
O=[inf,inf];
a=Point.a;
p=Point.q;
k=Point.k;
if k>1
    P=[mod(-Point.x,p) Point.y/sqrt(-1)];
else
    P=[Point.x Point.y];
end
if prod(P==O)
    n=1;
    modified_Point.order=n;
    return
end
Q=EC_add(Point,Point);
if prod([Q.x Q.y]==O)
    n=2;
    modified_Point.order=n;
    return
end
for n=3:p+1
    Q=EC_add(Point,Q);
    if prod([Q.x Q.y]==O)
        modified_Point.order=n;
        return
    end
end
if prod([Q.x Q.y]==O)==0
    n=inf;
    modified_Point.order=n;
end
end

