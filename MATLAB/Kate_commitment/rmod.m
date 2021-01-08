function [ Y ] = rmod( X,q )
% Take modular on rational numbers
% rmod: rational number -> integer in Fq

Y=zeros(size(X,1),size(X,2));
for i=1:size(X,1)
    for k=1:size(X,2)
        x=X(i,k);
        if round(x)==x
            y=mod(x,q);
        else
            [n,d]=rat(x);
            y=mod(n*MODinv(d,q),q);
        end
        Y(i,k)=y;
    end
end
end

