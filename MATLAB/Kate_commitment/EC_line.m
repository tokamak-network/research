function [out] = EC_line(Point1,Point2)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
% output: g(x,y)=cy+dx+e

if Point1.k ~= Point2.k
    error('mismatched degrees')
end
a=Point1.a;
p=Point1.q;
k=Point1.k;
if k>1
    P=[cmod(-Point1.x,p) Point1.y/sqrt(-1)];
    Q=[cmod(-Point2.x,p) Point2.y/sqrt(-1)];
else
    P=[Point1.x Point1.y];
    Q=[Point2.x Point2.y];
end

xp=P(1);
xq=Q(1);
yp=P(2);
yq=Q(2);

O=[inf,inf];
if prod(P==O) && prod(Q==O)
    error('Both input points are Point at Infinity')
end

    

if prod(P==Q) && yp~=0
    %tangent
    if yp==inf
        'fsadfsdf'
    end
    s=cmod((3*xp^2+a)*MODinv((2*yp),p),p);
    c=1;
    d=cmod(-s,p);
    e=cmod(s*xp-yp,p);
elseif xp==xq
    %vertical
    c=0;
    d=1;
    e=cmod(-xp,p);
elseif  prod(P==O) && ~prod(Q==O)
        %vertical
    c=0;
    d=1;
    e=cmod(-xq,p);
elseif  ~prod(P==O) && prod(Q==O)
        %vertical
    c=0;
    d=1;
    e=cmod(-xp,p);
else
    s=cmod((yq-yp)*MODinv((xq-xp),p),p);
    c=1;
    d=cmod(-s,p);
    e=cmod(s*xp-yp,p);
end

if k>1
    c=c/sqrt(-1);
    d=cmod(-d,p);
end

out=[c d e];

end

