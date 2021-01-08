%% Code written by Jehyuk Jang
% Instantation of Kate polynomial commitment protocol
% for single polynomial and single evaluation point.
% Last updated on Jan. 7.
% INFONET Lab., GIST, Republic of Korea
% Contact: jjh2014@gist.ac.kr
display('Note: This script supports a commitment only for a single polynomial with a single evluation point.')
display('---------------------------------------------------------------------')

clear
%% System params
p=71; % Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.
q=p^2-1; % Field size for polynomial.
k=2;
% Elliptic curve: y^2=x^3+a*x+0
a=1;
b=0;

%% Polynomial definition
degree=10; % In this code, the variable "degree" does not represent the hightest order of polynomial (mathematical degree), but the length of coefficients. That is, "degree"=(mathematical degree)+1.
syms X
poly_coeffs=randi(q,degree,1)-1; % from top to bottom, the highest degree to 0-degree
f(X)=repmat(X,1,degree).^(degree-1:-1:0)*poly_coeffs;
display('The function to commit: ')
display(f)
display('---------------------------------------------------------------------')

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
srs1=zeros(1,degree);
srs1(1)=1;
SRS1=repmat(g,1,degree);
for i=2:degree
    srs1(i)=mod(srs1(i-1)*x,q);
    SRS1(i)=EC_pmult(srs1(i),g);
end
srs2=[1 x];
SRS2=EC_pmult(srs2,h);

%% Prover: commit
display('Prover commit starts...')
tic;
commit=EC_polyeval(poly_coeffs,SRS1);
display('Commitment has been made.')
toc;
display('Commitment (EC coordinate (x,y)): ')
display(commit)
display('---------------------------------------------------------------------')
%% Prover: prove (make witness)
tic;
display('Prover starts to make witness...')
z=randi(q)-1;
claimed_output=0;
point=1;
for i=1:degree
    if i>1
        point=mod(point*z,q);
    end
    claimed_output=mod(claimed_output+poly_coeffs(degree+1-i)*point,q);
end

numer(X)=f(X)+mod(-claimed_output,q);
denom(X)=X+mod(-z,q);
H(X)=polydiv(numer(X),denom(X),q);
H_coeffs=double(coeffs(H)); %from 0-degree to the highest degree
H_coeffs=flip(H_coeffs);
proof=EC_polyeval(H_coeffs,SRS1);
display('Witness has been made.')
toc;
display('Polynomial evaluation result:')
display(claimed_output)
display('Evaluation point at: ')
display(z)
display('Witness (EC coordinate (x,y)): ')
display([proof.x proof.y])
display('---------------------------------------------------------------------')

%% (debuging code)
f_eval=0;
for i=1:degree
    f_eval=mod(f_eval+poly_coeffs(degree+1-i)*srs1(i),q);
end
lhs=mod(f_eval-claimed_output,q);
H_eval=0;
for i=1:length(H_coeffs)
    H_eval=mod(H_eval+H_coeffs(length(H_coeffs)+1-i)*srs1(i),q);
end
rhs=mod(H_eval*(x-z),q);
debug=lhs==rhs;

%% Verifier: open and verify
display('Verification starts...')
tic;
CLAIMED_OUTPUT=EC_pmult(claimed_output,g);
LHS=cmod(weil(EC_add(commit,EC_inv(CLAIMED_OUTPUT)),h,Group1,Group2),p);
XminusZ=EC_add(SRS2(2),EC_inv(EC_pmult(z,h)));
RHS=cmod(weil(proof,XminusZ,Group1,Group2),p);
result=LHS==RHS;
display('Verification completes.')
toc;
display(LHS)
display(RHS)
if result==1
    display('Verification is successful.')
else
    display('Verification failure')
end