function [ out ] =eval_f1(T,P,R,a,p )
% Eval f1 at the point T
% div(f1)=(P+R)-(R)-(P)+(O)

O=[inf,inf];
M=EC_add(P,R,a,p);
if prod(EC_inv(M,p)==T)
    'fdsafe'
end
g1=EC_line(P,R,a,p);
if prod(M==O)
    g2=[0, 0, 1];
else
    g2=EC_line(M,EC_inv(M,p),a,p);
end
out=mod(eval_line(g2,T,p)*MODinv(eval_line(g1,T,p),p),p);
if isnan(out)
    'fsdafsadf'
end
end

