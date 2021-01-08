function [ out ] = EC_polyeval( poly_coeffs,SRS )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
if length(SRS)<length(poly_coeffs)
    error('Not enough length of SRS');
end
degree=length(poly_coeffs);
sum=SRS(1);
sum.x=inf;
sum.y=inf;
poly_coeffs=flip(poly_coeffs); % now from to to bottol, 0-degree to the highest degree
for i=1:degree
    temp=EC_pmult(poly_coeffs(i),SRS(i));
    sum=EC_add(sum,temp);
end
out=sum;
end

