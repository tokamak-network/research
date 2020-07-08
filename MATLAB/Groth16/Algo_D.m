function [ out ] = Algo_D(T,f_b,f_c,Pb,Pc)
% evaluate f_{b+c} at the point T
p=T.q;
O=[inf,inf];
if prod([Pb.x Pb.y]==O) || prod([Pc.x Pc.y]==O)
    out=cmod(f_b*f_c,p);
    return
end   
Pd=EC_add(Pb,Pc);
g1=EC_line(Pb,Pc);
if prod([Pd.x Pd.y]==O)
    g2=[0,0,1];
else
    g2=EC_line(Pd,EC_inv(Pd));
end
% if Peq(T,Pd)
%     'fsdafer'
% end
if length(g1)~=3 || length(g2)~=3
    'fsdafef'
end
out=cmod(f_b*f_c*eval_line(g1,T)*MODinv(eval_line(g2,T),p),p);
end

