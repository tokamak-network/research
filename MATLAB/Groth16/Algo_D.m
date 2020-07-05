function [ out ] = Algo_D(T,f_b,f_c,Pb,Pc,a,p)
% evaluate f_{b+c} at the point T
O=[inf,inf];
if prod(Pb==O) || prod(Pc==O)
    out=mod(f_b*f_c,p);
    return
end   
Pd=EC_add(Pb,Pc,a,p);
g1=EC_line(Pb,Pc,a,p);
if prod(Pd==O)
    g2=[0,0,1];
else
    g2=EC_line(Pd,EC_inv(Pd,p),a,p);
end
if prod(T==Pd)
    'fsdafer'
end
if length(g1)~=3 || length(g2)~=3
    'fsdafef'
end
out=mod(f_b*f_c*eval_line(g1,T,p)*MODinv(eval_line(g2,T,p),p),p);
end

