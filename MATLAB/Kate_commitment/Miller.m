function [out]=Miller(n,T,P,R)

%Init
Z=P;
Z.x=inf;
Z.y=inf;
V=1;
k=0;
f1=eval_f1(T,P,R);
bstring=dec2bin(n);
m=length(bstring);
%Iter
for i=1:m
    if str2double(bstring(i))==1
        V=Algo_D(T,V,f1,Z,P);
        if isnan(V)
            'asdfsadf'
        end
        Z=EC_add(Z,P);
        k=k+1;
    end
    if i<m
        V=Algo_D(T,V,V,Z,Z);
        if isnan(V)
            'asdfsadf'
        end
        Z=EC_pmult(2,Z);
        k=2*k;
    end
end
out=V;

end