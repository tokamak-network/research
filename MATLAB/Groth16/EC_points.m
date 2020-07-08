function [ Group ] = EC_points( Curve)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
p=Curve.q;
a=Curve.a;
b=Curve.b;
x=0:p-1;
y=0:p-1;
[xx,yy]=meshgrid(x,y);
z=mod(yy.^2,p) - mod(xx.^3 + a*xx + b,p);
idxs=find(z == 0);
% your solutions are,
size=length(idxs);
Group(size)=Curve;
for i=1:size
    ref=idxs(i);
    Group(i)=Curve;
    Group(i).k=1;
    Group(i).x(1)=xx(ref);
    Group(i).y(1)=yy(ref);
    Group(i)=EC_order(Group(i));
end
%    P=[xx(idxs) yy(idxs)];
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

