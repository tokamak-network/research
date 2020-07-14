function [ Group2 ] = EC_extend( Group1 )
% Works only for curves of the form: y^2==x^3+ax with p==3mod4
% It is assumed k=2
p=Group1(1).q;
Group2=Group1;
size=length(Group1);
for i=1:size
    Group2(i).k=2;
    Group2(i).x=mod(-1*Group1(i).x,p);
    Group2(i).y=sqrt(-1)*Group1(i).y;
end


end

