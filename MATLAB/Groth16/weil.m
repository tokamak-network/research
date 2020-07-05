function [ Weil ] = weil(P,Q,En,a,p)
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here
n=size(En,1)+1;
bstring=dec2bin(n);
m=length(bstring);
K=[];
k=0;
for i=1:m
    if str2double(bstring(i))==1
        k=k+1;
        K=[K k];
    end
    if i<m
        k=2*k;
        K=[K k];
    end
end
RPset=[];
for i=1:size(En,1)
    RP=En(i,:);
    PpRP=EC_add(P,RP,a,p);
    flag=0;
    for j=1:length(K)
        k=K(j);
        flag=flag+prod(EC_pmult(k,Q,a,p)==RP)+prod(EC_pmult(k,Q,a,p)==PpRP)...
            +prod(EC_inv(EC_pmult(k,Q,a,p),p)==RP)...
            +prod(EC_inv(EC_pmult(k,Q,a,p),p)==PpRP);
    end
    if flag==0
        RPset=[RPset; RP];
    end
end

idx=randi(size(RPset,1));
RP=RPset(idx,:);
PpRP=EC_add(P,RP,a,p);


RQset=[];
for i=1:size(En,1)
    RQ=En(i,:);
    QpRQ=EC_add(Q,RQ,a,p);
    flag=0;
    for j=1:length(K)
        k=K(j);
        flag=flag+prod(EC_pmult(k,P,a,p)==RQ)+prod(EC_pmult(k,P,a,p)==QpRQ)...
            +prod(EC_inv(EC_pmult(k,P,a,p),p)==RQ)...
            +prod(EC_inv(EC_pmult(k,P,a,p),p)==QpRQ)...
            +prod(EC_inv(QpRQ,p)==RP)...
            +prod(EC_inv(PpRP,p)==RQ)...
            +prod(EC_inv(PpRP,p)==QpRQ)...
            +prod(EC_inv(QpRQ,p)==PpRP)...
            +prod(QpRQ==RP)...
            +prod(PpRP==RQ)...
            +prod(RP==RQ);
    end
    if flag==0
        RQset=[RQset; RQ];
    end
end
idx=randi(size(RQset,1));
RQ=RQset(idx,:);
QpRQ=EC_add(Q,RQ,a,p);


%A_P=P+RP-RP
%n*AP=n*(P+RP)+n*(-RP)


numer=Miller(n,QpRQ,P,RP,a,p)*Miller(n,RP,Q,RQ,a,p);
denom=Miller(n,RQ,P,RP,a,p)*Miller(n,PpRP,Q,RQ,a,p);
Weil=mod(mod(numer,p)*MODinv(denom,p),p);

end

