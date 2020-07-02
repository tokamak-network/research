p=5;
a=0;
b=1;
%G=[2,3];
P=[2,3];
Q=[24,0];

%If g, the generator of G used in Pinocchio must have the highest order
%(n=p+1), then |E_Fp|=|En|
%E_Fp = EC_points( a,b,p );
E_Fp2= EC_points( a,b,p^2);
%n=EC_order(G,a,p^2);
n=p+1;
En=[];
for i=1:size(E_Fp2,1)
    if rem(n,EC_order(E_Fp2(i,:),a,p^2))==0
        En=[En E_fp2(i,:)];
    end
end
% for i=1:size(E_Fp,1)
%     if rem(n,EC_order(E_Fp(i,:),a,p))==0
%         En=[En E_fp(i,:)];
%     end
% end

RP=P;
while prod(P==RP) || prod(RP==EC_inv(P,p^2))
%     idx=randi(size(E_Fp2,1));
%     RP=E_Fp2(idx,:);
    idx=randi(size(En,1));
    RP=En(idx,:);
end

RQ=Q;
while prod(Q==RQ) || prod(RQ==EC_inv(Q,p^2))
%     idx=randi(size(E_Fp2,1));
%     RQ=E_Fp2(idx,:);
    idx=randi(size(En,1));
    RQ=En(idx,:);
end

%A_P=P+RP-RP
%n*AP=n*(P+RP)+n*(-RP)
TP1=EC_pmult(p,EC_add(P,RP,a,p^2),a,p^2);
TP2=EC_pmult(n,EC_inv(RP,p^2),a,p^2);
if prod(isnan(TP1)),    error('TP1 is NaN');end
if prod(isnan(TP2)),    error('TP2 is NaN');end
[fpa,fpb]=EC_line(TP1,TP2,p^2);

TQ1=EC_pmult(n,EC_add(Q,RQ,a,p^2),a,p^2);
TQ2=EC_pmult(n,EC_inv(RQ,p^2),a,p^2);
if prod(isnan(TQ1)),    error('TQ1 is NaN');end
if prod(isnan(TQ2)),    error('TQ2 is NaN');end
[fqa,fqb]=EC_line(TQ1,TQ2,p^2);

result=EC_weil(P,Q,fpa,fpb,fqa,fqb,p^2);
