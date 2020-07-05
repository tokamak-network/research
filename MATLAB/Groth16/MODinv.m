function [ aINV ] = MODinv(a,n)
% The inverse of a modulo n
while a<0
    a=a+n;
end
t=0;
r=n;
newt=1;
newr=a;
while newr~=0
    Quotient=floor(r/newr);
    
    oldt=t;
    t=newt;
    newt= oldt-Quotient*newt;
    
    oldr=r;
    r=newr;
    newr=oldr-Quotient*newr;
    if isnan(newr)
        'fsdafe'
    end
end
if r>1
    aINV=NaN;
    return
end
if t<0
    t=t+n;
end
aINV=t;
end

