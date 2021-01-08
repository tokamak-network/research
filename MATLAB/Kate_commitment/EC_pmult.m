function [ Q ] = EC_pmult(p,Point)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
Q=[];
for L=1:length(p)
    out=Point;
    Q=[Q out];
    if p(L)==0
        Q(end).x=inf;
        Q(end).y=inf;
        continue
    elseif p(L)==1
        Q(end)=Point;
        continue
    end
    
    Q(end)=EC_add(Point,Point);
    for i=3:p(L)
        Q(end)=EC_add(Point,Q(end));
    end
end
end

