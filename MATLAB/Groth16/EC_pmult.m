function [ Q ] = EC_pmult(k,P,a,p)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
if k==0
    Q=[inf,inf];
    return
elseif k==1
    Q=P;
    return
end
    
Q=EC_add(P,P,a,p);
for i=1:k-2
    Q=EC_add(P,Q,a,p);
end
end

