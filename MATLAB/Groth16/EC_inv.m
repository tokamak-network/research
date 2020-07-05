function [ Q ] = EC_inv( P,p )
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here
O=[inf,inf];
if prod(P==O)
    Q=P;
elseif P(2)==0
    Q=[P(1), p];
else
    Q=[P(1), mod(-P(2),p)];
end

end

