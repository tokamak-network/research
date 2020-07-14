function [ out ] =eval_f1(T,P,R)
% Eval f1 at the point T
% div(f1)=(P+R)-(R)-(P)+(O)
p=T.q;
O=[inf,inf];
M=EC_add(P,R);
% if Peq(EC_inv(M),T)
%     'fdsafe'
% end
g1=EC_line(P,R);
if prod([M.x M.y]==O)
    g2=[0, 0, 1];
else
    g2=EC_line(M,EC_inv(M));
end
out=cmod(eval_line(g2,T)*MODinv(eval_line(g1,T),p),p);
if isnan(out)
    'fsdafsadf'
end
end

