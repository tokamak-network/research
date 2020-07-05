function [ k ] = EC_order( P,a,p )
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here
O=[inf,inf];
if prod(P==O)
    k=1;
    return
end
Q=EC_add(P,P,a,p);
if prod(Q==O)
    k=2;
    return
end
for k=3:p+1
    Q=EC_add(P,Q,a,p);
    if prod(Q==O)
        return
    end
end
if prod(Q==O)==0
    k=inf;
end
end

