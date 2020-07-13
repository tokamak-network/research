function [ aINV ] = MODinv(a,n)
% The inverse of a modulo n
if a==0
    error('divide by zero')
end
if imag(a)==0
    mult=1;
    b=a;
else
    mult=real(a)-imag(a)*sqrt(-1);
    b=real(a)^2+imag(a)^2;
end
if b==inf || b==-inf
    error('divide by inf or -inf')
end
while b<0
    b=b+n;
end
t=0;
r=n;
newt=1;
newr=b;
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
aINV=cmod(t*mult,n);
end

