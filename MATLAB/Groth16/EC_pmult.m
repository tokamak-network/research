function [ Q ] = EC_pmult(p,Point)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
Q=Point;
if p==0
    Q.x=inf;
    Q.y=inf;
    return
elseif p==1
    Q=Point;
    return
end
    
Q=EC_add(Point,Point);
for i=3:p
    Q=EC_add(Point,Q);
end
end

