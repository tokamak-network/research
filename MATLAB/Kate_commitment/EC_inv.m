function [ Point2 ] = EC_inv( Point)
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here
p=Point.q;
P=[Point.x Point.y];
Point2=Point;
O=[inf,inf];
if prod(P==O)
    Q=P;
elseif P(2)==0
    if Point.k>1
        Q=[P(1), p*sqrt(-1)];
    else
        Q=[P(1), p];
    end
else
    Q=[P(1), cmod(-P(2),p)];
end
Point2.x=Q(1);
Point2.y=Q(2);
end

