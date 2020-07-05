function [out]=Miller(n,T,P,R,a,p)

%Init
Z=[inf,inf];
V=1;
k=0;
f1=eval_f1(T,P,R,a,p);
bstring=dec2bin(n);
m=length(bstring);
%Iter
for i=1:m
    if str2double(bstring(i))==1
        V=Algo_D(T,V,f1,Z,P,a,p);
        if isnan(V)
            'asdfsadf'
        end
        Z=EC_add(Z,P,a,p);
        k=k+1;
    end
    if i<m
        V=Algo_D(T,V,V,Z,Z,a,p);
        if isnan(V)
            'asdfsadf'
        end
        Z=EC_pmult(2,Z,a,p);
        k=2*k;
    end
end
out=V;

end