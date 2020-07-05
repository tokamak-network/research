function [ R ] = EC_add( P,Q,a,p)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
if prod(isnan(P)) || prod(isnan(Q))
	R=[nan, nan];
	return
end
O=[inf,inf];
if prod([P,Q]==[O,O])
    R=O;
    return
else
    if prod(P==O)
        R=Q;
        return
    elseif prod(Q==O)
        R=P;
        return
    end
end
    
xp=P(1);
xq=Q(1);
yp=P(2);
yq=Q(2);
if xp~=xq
    s=mod((yq-yp)*MODinv((xq-xp),p),p);
else
    if yp~=yq
        R=O;
        return
    else
        if yp==0
            R=O;
            return
        else
            s=mod((3*xp^2+a)*MODinv((2*yp),p),p);
        end
    end
end
xr=mod(s^2-xp-xq,p);
yr=mod(s*(xp-xr)-yp,p);
R=[xr,yr];
end

