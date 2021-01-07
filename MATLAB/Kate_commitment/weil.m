function [ Weil ] = weil(Point1,Point2,G1,G2)
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here
a=Point1.a;
p=Point1.q;
P=Point1;
Q=Point2;
n=G1(1).gen.order;

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
% RPset=[];
% for i=1:length(G1)
%     RP=G1(i);
%     PpRP=EC_add(P,RP);
%     flag=0;
%     for j=1:length(K)
%         k=K(j);
%         flag=flag+Peq(EC_pmult(k,Q),RP)+Peq(EC_pmult(k,Q),PpRP)...
%             +Peq(EC_inv(EC_pmult(k,Q)),RP)...
%             +Peq(EC_inv(EC_pmult(k,Q)),PpRP);
%     end
%     if flag==0
%         RPset=[RPset RP];
%     end
% end

% idx=randi(length(RPset));
% RP=RPset(idx);
RP=P;
PpRP=EC_add(P,RP);
while Peq(RP,P) || prod([PpRP.x PpRP.y]==[inf inf])
    idx=randi(n-1);
    RP=G1(idx);
    PpRP=EC_add(P,RP);
end

% RQset=[];
% for i=1:length(G2)
%     RQ=G2(i);
%     QpRQ=EC_add(Q,RQ);
%     flag=0;
%     for j=1:length(K)
%         k=K(j);
%         flag=flag+Peq(EC_pmult(k,P),RQ)+Peq(EC_pmult(k,P),QpRQ)...
%             +Peq(EC_inv(EC_pmult(k,P)),RQ)...
%             +Peq(EC_inv(EC_pmult(k,P)),QpRQ)...
%             +Peq(EC_inv(QpRQ),RP)...
%             +Peq(EC_inv(PpRP),RQ)...
%             +Peq(EC_inv(PpRP),QpRQ)...
%             +Peq(EC_inv(QpRQ),PpRP)...
%             +Peq(QpRQ,RP)...
%             +Peq(PpRP,RQ)...
%             +Peq(RP,RQ);
%     end
%     if flag==0
%         RQset=[RQset; RQ];
%     end
% end
% idx=randi(size(RQset,1));
% RQ=RQset(idx,:);
RQ=Q;
QpRQ=EC_add(Q,RQ);
while Peq(RQ,Q) || prod([QpRQ.x QpRQ.y]==[inf inf])
    idx=randi(n-1);
    RQ=G2(idx);
    QpRQ=EC_add(Q,RQ);
end


%A_P=P+RP-RP
%n*AP=n*(P+RP)+n*(-RP)


numer=cmod(Miller(n,QpRQ,P,RP),p)*cmod(Miller(n,RP,Q,RQ),p);
denom=cmod(Miller(n,RQ,P,RP),p)*cmod(Miller(n,PpRP,Q,RQ),p);
Weil=cmod(cmod(numer,p)*MODinv(denom,p),p);

end

