function [ P ] = EC_points( a,b,p)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
x=0:p-1;
y=0:p-1;
[xx,yy]=meshgrid(x,y);
z=mod(yy.^2,p) - mod(xx.^3 + a*xx + b,p);
idxs=find(z == 0);
% your solutions are,
P=[xx(idxs) yy(idxs)];
% P=[];
% for x=0:p-1
%     for y=0:p-1
%         if mod(y^2,p)-mod(x^3 + a*x + b,p)==0
%             if rem(n,EC_order([x,y],a,p))==0
%                 P=[P; [x,y]];
%             end
%         end
%     end
% end
end

