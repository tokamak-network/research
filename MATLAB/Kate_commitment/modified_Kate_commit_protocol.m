%% Code written by Jehyuk Jang
% Last updated on Jan. 5.
% INFONET Lab., GIST, Republic of Korea
% Contact: jjh2014@gist.ac.kr

clear
%% System params
p=71; % Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.
q=p^2-1; % Field size for program, R1CS, and QAP.
k=2;
% Elliptic curve: y^2=x^3+a*x+0
a=1;
b=0;

%% Polynomial definition
degree=3;   % For high levels of degree, precision errors occur.
syms X
coeffs=randi(q,degree,1)-1;
f(X)=repmat(X,1,degree).^(degree-1:-1:0)*coeffs;

%% Elliptic curve definition
Curve=struct();
Curve.q=p;
Curve.k=1;
Curve.a=a;
Curve.b=b;
Curve.x=0;
Curve.y=0;
Curve.order=0;
Curve.gen=Curve;

Group1=EC_points(Curve);
Group2=EC_extend(Group1);
Orders=zeros(1,length(Group1));
for i=1:length(Group1)
    Orders(i)=Group1(i).order;
end
% n is order of EC curve group
[n, ind]=max(Orders);
% g is a generator of EC curve group
g=Group1(ind);
% h is a generator of twisted curve group
h=Group2(ind);
g=rmfield(g,'gen');
h=rmfield(h,'gen');
for i=1:length(Group1)
    Group1(i).gen=g;
    Group2(i).gen=h;
end
PointInf1=g;
PointInf1.x=inf;
PointInf1.y=inf;
PointInf2=h;
PointInf2.x=inf;
PointInf2.y=inf;

%% Setup by trusted third party
x=randi(q)-1;
srs1=mod(repmat(x,1,degree).^(0:degree-1),q);
srs2=[1 x];
SRS1=EC_pmult(srs1,g);
SRS2=EC_pmult(srs2,h);

%% Prover: commit
f_eval=mod(double(f(x)),q);
commit=EC_pmult(f_eval,g);  %% must use srs
z=randi(q)-1;
while gcd(mod(x-z,q),q)~=1
    z=randi(q)-1;
end
s=mod(double(f(z)),q);

%% Verifier: open
gamma=randi(q)-1;

%% Prover: prove
H=mod(gamma*mod(mod(double(f(x))-double(f(z)),q)*MODinv(x-z,q),q),q); %% must use srs
W=EC_pmult(H,g);

%% (debuging code)
lhs=mod(gamma*(f_eval-s),q);
rhs=mod(H*(x-z),q);
debug=lhs==rhs;

%% Verifier: verify
F=EC_pmult(gamma,commit);
v=EC_pmult(mod(gamma*s,q),g);
LHS=cmod(weil(EC_add(F,EC_inv(v)),h,Group1,Group2),p);
RHS=cmod(weil(W,EC_pmult(mod(x-z,q),h),Group1,Group2),p);
result=LHS==RHS;
