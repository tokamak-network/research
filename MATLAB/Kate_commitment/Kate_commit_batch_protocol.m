%% Code written by Jehyuk Jang
% Instantation of Kate polynomial commitment protocol
% with batch opening (single polynomial with multiple evaluation points).
% Last updated on Jan. 8.
% INFONET Lab., GIST, Republic of Korea
% Contact: jjh2014@gist.ac.kr
display('Note: This script supports a commitment for a single polynomial with multiple evluation points.')
display('---------------------------------------------------------------------')

clear
%% System params
p=71; % Field size for elliptic curve arithmetic. Choose any prime p such that mod(p,4)==3.
q=p^2-1; % Field size for polynomial.
k=2;
% Elliptic curve: y^2=x^3+a*x+0
a=1;
b=0;
Num_eval=4;

%% Polynomial definition
degree=10; % In this code, the variable "degree" does not represent the hightest order of polynomial (mathematical degree), but the length of coefficients. That is, "degree"=(mathematical degree)+1.
syms X
poly_coeffs=randi(q,degree,1)-1; % from top to bottom, the highest degree to 0-degree
f(X)=repmat(X,1,degree).^(degree-1:-1:0)*poly_coeffs;

if Num_eval>=degree
    error('Too many evaluation points, which implies the disclosure of polynomial. Set to Num_eval < degree')
end

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
srs2=zeros(1,Num_eval+1);
srs2(1)=1;
SRS2=repmat(h,1,Num_eval+1);
for i=2:Num_eval+1
    srs2(i)=mod(srs2(i-1)*x,q);
    SRS2(i)=EC_pmult(srs2(i),h);
end

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
eval_points=randi(q,1,Num_eval)-1;
if length(eval_points)~=length(unique(eval_points))
    eval_points=randi(q,1,Num_eval)-1;
end
claimed_outputs=zeros(1,Num_eval);
points=ones(1,Num_eval);
for i=1:degree
    if i>1
        points=mod(points.*eval_points,q);
    end
    claimed_outputs=mod(claimed_outputs+poly_coeffs(degree+1-i).*points,q);
end
numer(X)=f(X);
denom(X)=sym(1);
for i=1:Num_eval
    denom(X)=pmod(denom(X)*(X-eval_points(i)),q);
end
[Q(X), R(X)]=polydiv(numer(X),denom(X),q);
H(X)=polydiv(f(X)-R(X),denom(X),q);
H_coeffs=flip(double(coeffs(H))); %from the highest degree to 0-degree
proof=EC_polyeval(H_coeffs,SRS1);
R_coeffs=flip(double(coeffs(R))); % This polynomial R(X) is replaced with "claimed evaluation results". Mathematically, for all evaluation points z_i, R(z_i)=f(z_i).
display('Witness has been made.')
toc;
display('Claimed polynomial evaluation results: ')
display(claimed_outputs)
display('Coefficients of R(X): ')
display(R_coeffs)
display('Evaluation points: ')
display(eval_points)
display('Witness (EC coordinate (x,y)): ')
display([proof.x proof.y])
disp(['The length of proofs is: ', num2str(length(claimed_outputs)*2+length(R_coeffs)), ' numbers + 1 EC coordinate.'])
display('---------------------------------------------------------------------')

%% (debuging code)
debug1=1;
for i=1:Num_eval
    debug1=debug1*(mod(double(R(eval_points(i))),q)==claimed_outputs(i));
end
f_eval=0;
for i=1:degree
    f_eval=mod(f_eval+poly_coeffs(degree+1-i)*srs1(i),q);
end
R_eval=0;
for i=1:length(R_coeffs)
    R_eval=mod(R_eval+R_coeffs(length(R_coeffs)+1-i)*srs1(i),q);
end
lhs=mod(f_eval-R_eval,q);
H_eval=0;
for i=1:length(H_coeffs)
    H_eval=mod(H_eval+H_coeffs(length(H_coeffs)+1-i)*srs1(i),q);
end
rhs=H_eval;
for i=1:Num_eval
    rhs=mod(rhs*(x-eval_points(i)),q);
end
debug2=lhs==rhs;

%% Verifier: open and verify
display('Verification starts...')
tic;
R_eval=0;
for i=1:length(R_coeffs)
    R_eval=mod(R_eval+R_coeffs(length(R_coeffs)+1-i)*srs1(i),q);
end
LHS=cmod(weil(EC_add(commit,EC_inv(EC_pmult(R_eval,g))),h,Group1,Group2),p);
zero_poly(X)=sym(1);
for i=1:Num_eval
    zero_poly(X)=pmod(zero_poly(X)*(X-eval_points(i)),q);
end
zero_coeffs=flip(coeffs(zero_poly(X)));
ZERO_POLY=EC_polyeval(zero_coeffs,SRS2);
RHS=cmod(weil(proof,ZERO_POLY,Group1,Group2),p);

display('Verification completes.')
toc;
display(LHS)
display(RHS)
result=1;
result=result*(LHS==RHS);
result=result*(Num_eval==length(R_coeffs));
R_point_evals=zeros(1,Num_eval);
points=ones(1,Num_eval);
for i=1:Num_eval
    if i>1
        points=mod(points.*eval_points,q);
    end
    R_point_evals=mod(R_point_evals+R_coeffs(length(R_coeffs)+1-i).*points,q);
end
result=result*prod(R_point_evals==claimed_outputs);
display('R(X) is valid')
if result==1
    display('Verification is successful.')
else
    display('Verification failure')
end

