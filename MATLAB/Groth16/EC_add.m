function [ R ] = EC_add( Point1,Point2)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
if Point1.k ~= Point2.k
    error('mismatched degrees')
end
R=Point1;
a=Point1.a;
p=Point1.q;
k=Point1.k;

P=[Point1.x Point1.y];
Q=[Point2.x Point2.y];

if prod(isnan(P)) || prod(isnan(Q))
	R.x=nan;
    R.y=nan;
	return
end
O=[inf,inf];
if prod([P,Q]==[O,O])
    R.x=inf;
    R.y=inf;
    return
else
    if prod(P==O)
        R=Point2;
        return
    elseif prod(Q==O)
        R=Point1;
        return
    end
end

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
if xp~=xq
    s=cmod((yq-yp)*MODinv((xq-xp),p),p);
else
    if yp~=yq
        R.x=inf;
        R.y=inf;
        return
    else
        if yp==0
            R.x=inf;
            R.y=inf;
            return
        else
            s=cmod((3*xp^2+a)*MODinv((2*yp),p),p);
        end
    end
end
xr=cmod(s^2-xp-xq,p);
yr=cmod(s*(xp-xr)-yp,p);

if k>1
    R.x=cmod(-xr,p);
    R.y=yr*sqrt(-1);
else
    R.x=xr;
    R.y=yr;
end
end

