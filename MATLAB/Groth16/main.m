%% Code written by Jehyuk Jang
% Last updated on 6th July
% INFONET Lab., GIST, Republic of Korea
% Contact: jjh2014@gist.ac.kr

clear
%% System Params
q=41;
% Elliptic curve: y^2=x^3+a*x+b
a=0;
b=1;
Points=EC_points(a,b,q);
PwOrders=[Points zeros(size(Points,1),1)];
for i=1:size(Points,1)
    PwOrders(i,3)=EC_order(Points(i,:),a,q);
end
% n is order of EC curve group
[n, ind]=max(PwOrders(:,3));
% g is a generator of EC curve group
g=PwOrders(ind,[1,2]);
% h is a generator of twisted curve group
h=g;

En=zeros(n-1,2);
En(1,:)=g;
for i=2:n-1
    En(i,:)=EC_add(En(i-1,:),g,a,q);
end

%% From function to R1CS

A=[[0, 1, 0, 0, 0, 0];
[0, 0, 0, 1, 0, 0];
[0, 1, 0, 0, 1, 0];
[5, 0, 0, 0, 0, 1]].';
B=[[0, 1, 0, 0, 0, 0];
[0, 1, 0, 0, 0, 0];
[1, 0, 0, 0, 0, 0];
[1, 0, 0, 0, 0, 0]].';
C=[[0, 0, 0, 1, 0, 0];
[0, 0, 0, 0, 1, 0];
[0, 0, 0, 0, 0, 1];
[0, 0, 1, 0, 0, 0]].';

Z=[24, -50, 35, -10, 1];
R=[1, 3, 35, 9, 27, 30];
% 1 and 3 are inputs; 3 is the output; the rests are intermediate values
Ind_mid=[4 5 6];
Ind_IO=[1 2 3];

% # of wires= size of circuit (m)
NumWires=size(A,1);
% # of gates= degree of circuit (d)
NumGates=size(A,2);
%% From R1CS to QAP
Ap=[[-5.0, 9.166666666666666, -5.0, 0.8333333333333334];
[8.0, -11.333333333333332, 5.0, -0.6666666666666666];
[0.0, 0.0, 0.0, 0.0];
[-6.0, 9.5, -4.0, 0.5];
[4.0, -7.0, 3.5, -0.5];
[-1.0, 1.8333333333333333, -1.0, 0.16666666666666666]];

Bp=[[3.0, -5.166666666666667, 2.5, -0.33333333333333337];
[-2.0, 5.166666666666667, -2.5, 0.33333333333333337];
[0.0, 0.0, 0.0, 0.0];
[0.0, 0.0, 0.0, 0.0];
[0.0, 0.0, 0.0, 0.0];
[0.0, 0.0, 0.0, 0.0]];

Cp=[[0.0, 0.0, 0.0, 0.0];
[0.0, 0.0, 0.0, 0.0];
[-1.0, 1.8333333333333333, -1.0, 0.16666666666666666];
[4.0, -4.333333333333333, 1.5, -0.16666666666666666];
[-6.0, 9.5, -4.0, 0.5];
[4.0, -7.0, 3.5, -0.5]];

Ap=rmod(Ap,q);
Bp=rmod(Bp,q);
Cp=rmod(Cp,q);
Zorig=Z;
Z=rmod(Z,q);
R=rmod(R,q);

m=size(Ap,1);
d=size(Ap,2);

% generate polynomials in variable x from their coefficient vectors
syms x
xv=[];
for k=0:d-1
    xv=[xv; x^k];
end
Ax=Ap*xv;
Bx=Bp*xv;
Cx=Cp*xv;

xv=[xv;x^d];
Zx=Z*xv;
Zx_orig=Zorig*xv;
Zx_roots=double(root(Zx_orig));

% P(x)=linear_combination(r,Ax)*linear_combination(r,Bx)-linear_combination(r,Cx)
Px=(R*Ax)*(R*Bx)-(R*Cx);
Px=simplify(Px);
Px=pmod(Px,q);

% Check the validity of P(x)
checksum=0;
for i=Zx_roots
    checksum=checksum+mod(double(subs(Px,x,i)),q);
end
display('QAP result:')
if checksum==0
    display('Px is valid')
else
    display('Invalid Px, check the Lagrange interpolation')
end

% find H(x) such that P(x)=H(x)*Z(x)
[Hx, rem]=polydiv(Px,Zx,q);
Hx=simplify(Hx);
Hx=pmod(Hx,q);

if rem==sym(0)
    display('Hx is valid')
else
    display('Invalid Hx')
end

%% Setup
alpha=1+randi(q-2);
beta=1+randi(q-2);
gamma=1+randi(q-2);
delta=1+randi(q-2);
x_val=1;
check=1:d;
while ismember(x_val,check)
    x_val=randi(q-1);
end
tau=[alpha beta gamma delta x_val];
Ax_val=rmod(double(subs(Ax,x,x_val)),q);
Bx_val=rmod(double(subs(Bx,x,x_val)),q);
Cx_val=rmod(double(subs(Cx,x,x_val)),q);
Zx_val=rmod(double(subs(Zx,x,x_val)),q);
Hx_val=rmod(double(subs(Hx,x,x_val)),q);

sigma1_1=[EC_pmult(alpha,g,a,q);
    EC_pmult(beta,g,a,q);
    EC_pmult(delta,g,a,q)];
sigma1_2=zeros(NumGates,2);
for i=0:NumGates-1
    val=mod(x_val^i,q);
    sigma1_2(i+1,:)=EC_pmult(val,g,a,q);
end
sigma1_3=zeros(numel(Ind_IO),2);
for i=Ind_IO
    val=mod((beta*Ax_val(i)+alpha*Bx_val(i)+Cx_val(i))*MODinv(gamma,q),q);
    sigma1_3(i,:)=EC_pmult(val,g,a,q);
end
sigma1_4=zeros(NumWires,2);
for i=Ind_mid
    val=mod((beta*Ax_val(i)+alpha*Bx_val(i)+Cx_val(i))*MODinv(delta,q),q);
    sigma1_4(i,:)=EC_pmult(val,g,a,q);
end
sigma1_5=zeros(NumGates-1,2);
for i=0:NumGates-2
    val=mod(x_val^i*MODinv(delta,q),q);
    sigma1_5(i+1,:)=EC_pmult(val,g,a,q);
end
sigma2_1=[EC_pmult(beta,h,a,q);
    EC_pmult(gamma,h,a,q);
    EC_pmult(delta,h,a,q)];
sigma2_2=zeros(NumGates,2);
for i=0:NumGates-1
    val=mod(x_val^i,q);
    sigma2_2(i+1,:)=EC_pmult(val,h,a,q);
end

%% Prove
% r and s are secret
r=randi(q-1);
s=randi(q-1);

A=mod(alpha+R(Ind_IO)*Ax_val(Ind_IO)+r*delta,q);
B=mod(beta+R(Ind_IO)*Bx_val(Ind_IO)+s*delta,q);
C=mod(MODinv(delta,q)*(R(Ind_mid)*(beta*Ax_val(Ind_mid)+alpha*Bx_val(Ind_mid)+Cx_val(Ind_mid))+Hx_val*Zx_val)...
    +A*s+B*r-r*s*delta,q);
% proof is denoted as pi in Groth16
proof=[EC_pmult(A,g,a,q);
    EC_pmult(C,g,a,q);
    EC_pmult(B,h,a,q)];

%% Verify
% e(A*g, B*h)
LHS=weil(proof(1,:),proof(3,:),En,a,q);
RHS=1;
% e(alpha*g, beta*h)
RHS=mod(RHS*weil(sigma1_1(1,:),sigma2_1(1,:),En,a,q),q);
for i=Ind_IO
    RHS=mod(RHS*weil(sigma1_3(i,:),sigma2_1(2,:),En,a,q)^R(i),q);
end
% e(C*g, delta*h)
RHS=mod(RHS*weil(proof(2,:),sigma2_1(3,:),En,a,q),q);
VfyResult=LHS==RHS;