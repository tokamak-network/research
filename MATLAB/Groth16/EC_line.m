function [ out ] = EC_line(P,Q,a,p)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
% output: g(x,y)=cy+dx+e
xp=P(1);
xq=Q(1);
yp=P(2);
yq=Q(2);
% O=[inf,inf];
% if prod(P==O) && prod(Q==O)
%     out=[0,0,1];
%     return
% end
% 
% if xor(prod(P==O),prod(Q==O))
%     error('invalid divisor')
% end
    

if prod(P==Q) && yp~=0
    %tangent
    if yp==inf
        'fsadfsdf'
    end
    s=mod((3*xp^2+a)*MODinv((2*yp),p),p);
elseif xp==xq
    %vertical
    c=0;
    d=1;
    e=mod(-xp,p);
    out=[c,d,e];
    return
else
    s=mod((yq-yp)*MODinv((xq-xp),p),p); 
end
c=1;
d=mod(-s,p);
e=mod(s*xp-yp,p);
out=[c,d,e];
end

