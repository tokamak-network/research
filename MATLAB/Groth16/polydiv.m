function [ quo, rem ] = polydiv( A,B,q )
% Divide a poly A by a poly B over Fq
% A/B (modq)
x=symvar(A);
[cA,tA]=coeffs(A);
[cB,tB]=coeffs(B);
target=sym(1);
degA=0;
while double(subs(tA(1)/target,x,2))~=1
    degA=degA+1;
    target=target*x;
end

target=sym(1);
degB=0;
while double(subs(tB(1)/target,x,2))~=1
    degB=degB+1;
    target=target*x;
end

if degA<degB
    quo=sym(0);
    rem=A;
else
    degdiff=degA-degB;
    cquo=zeros(1,degdiff+1);
    tquo=[];
    for i=degdiff:-1:0
        tquo=[tquo x^i];
    end
    
    rem=A;
    
    for i=1:length(cquo)
        [c,t]=coeffs(rem);
        if double(tB(1)*tquo(i)==t(1))
            cquo(i)=mod(c(1)*MODinv(cB(1),q),q);
            rem=pmod(rem-cquo(i)*tquo(i)*B,q);
        else
            cquo(i)=0;
        end
    end
    
    quo=pmod(cquo*tquo.',q);
    
end
end

