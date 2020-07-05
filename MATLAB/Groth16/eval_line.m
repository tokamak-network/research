function [ out ] = eval_line( g,P,p )
%target line G(x,y)=g(1)y+g(2)x+g(3)
%eval point P=(x,y);

xp=P(1);
yp=P(2);
out=mod(g(1)*yp+g(2)*xp+g(3),p);
end

