%% Code written by Jehyuk Jang
% Last updated on 6th July
% INFONET Lab., GIST, Republic of Korea
% Contact: jjh2014@gist.ac.kr

clear
%% System Params
p=71; % Choose any prime p such that mod(p,4)==3.
q=p^2-1;
k=2;
% Elliptic curve: y^2=x^3+a*x+0
a=1;
b=0;

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

% En=zeros(n-1,2);
% En(1,:)=g;
% for i=2:n-1
%     En(i,:)=EC_add(En(i-1,:),g,a,q);
% end

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

% # of wires= size of circuit (m)
NumWires=size(A,1);
% # of gates= degree of circuit (d)
NumGates=size(A,2);

Roots_of_Z=1:NumGates;
Z=[24, -50, 35, -10, 1];
R=[1, 3, 35, 9, 27, 30];
% 1 and 3 are inputs; 3 is the output; the rests are intermediate values
Ind_mid=[4 5 6];
Ind_IO=[1 2 3];


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

[NUM,DEN]=rat([Ap;Bp;Cp]);
denoms=unique(DEN);
mul=1;
for i=1:length(denoms)
    mul=lcm(mul,denoms(i));
end
Ap=Ap*mul;
Bp=Bp*mul;
Cp=Cp*mul^2;
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

% Debuging code: Check the validity of P(x)
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
Hp=coeffs(Hx);

if rem==sym(0)
    display('Hx is valid')
else
    display('Invalid Hx')
end

%% Setup
alpha=1+randi(q-2);
beta=1+randi(q-2);
gamma=1+randi(q-2);
while gcd(gamma,q)~=1
    gamma=1+randi(q-2);
end
delta=1+randi(q-2);
while gcd(delta,q)~=1
    delta=1+randi(q-2);
end
x_val=1;
while ismember(x_val,Roots_of_Z)
    x_val=randi(q-1);
end
% tau is secret
tau=[alpha beta gamma delta x_val];

Ax_val=rmod(double(subs(Ax,x,x_val)),q);
Bx_val=rmod(double(subs(Bx,x,x_val)),q);
Cx_val=rmod(double(subs(Cx,x,x_val)),q);
Zx_val=rmod(double(subs(Zx,x,x_val)),q);
Hx_val=rmod(double(subs(Hx,x,x_val)),q);

sigma1_1=[EC_pmult(alpha,g);
    EC_pmult(beta,g);
    EC_pmult(delta,g)];
sigma1_2(NumGates)=g;
for i=0:NumGates-1
    val=mod(x_val^i,q);
    sigma1_2(i+1)=EC_pmult(val,g);
end
sigma1_3(NumWires)=g;
VAL=zeros(1,NumWires);
for i=Ind_IO
    VAL(i)=mod((beta*Ax_val(i)+alpha*Bx_val(i)+Cx_val(i))*MODinv(gamma,q),q);
    sigma1_3(i)=EC_pmult(VAL(i),g);
end
sigma1_4(NumWires)=g;
for i=Ind_mid
    val=mod((beta*Ax_val(i)+alpha*Bx_val(i)+Cx_val(i))*MODinv(delta,q),q);
    sigma1_4(i)=EC_pmult(val,g);
end
sigma1_5(NumGates-1)=g;
for i=0:NumGates-2
    val=mod(x_val^i*MODinv(delta,q)*Zx_val,q);
    sigma1_5(i+1)=EC_pmult(val,g);
end
sigma2_1=[EC_pmult(beta,h);
    EC_pmult(gamma,h);
    EC_pmult(delta,h)];
sigma2_2(NumGates)=h;
for i=0:NumGates-1
    val=mod(x_val^i,q);
    sigma2_2(i+1)=EC_pmult(val,h);
end


%% Debuging code: Check that Polys and Coeffs are good

if mod(R*Ax_val*R*Bx_val-R*Cx_val,q)==mod(Zx_val*Hx_val,q)
    disp('Polys and Coeffs are verifiable')
else
    disp('Polys are not good')
end

%% Prove
% Generate r and s, which are secret
r=randi(q-1);
s=randi(q-1);


% Make proof
Proof_A=sigma1_1(1);
for i=1:NumWires
    temp=PointInf1;
    for j=0:NumGates-1
        temp=EC_add(temp,EC_pmult(Ap(i,j+1),sigma1_2(j+1)));
    end
    Proof_A=EC_add(Proof_A,EC_pmult(R(i),temp));
end
Proof_A=EC_add(Proof_A,EC_pmult(r,sigma1_1(3)));

Proof_B=sigma2_1(1);
for i=1:NumWires
    temp=PointInf2;
    for j=0:NumGates-1
        temp=EC_add(temp,EC_pmult(Bp(i,j+1),sigma2_2(j+1)));
    end
    Proof_B=EC_add(Proof_B,EC_pmult(R(i),temp));
end
Proof_B=EC_add(Proof_B,EC_pmult(s,sigma2_1(3)));

temp_Proof_B=sigma1_1(2);
for i=1:NumWires
    temp=PointInf1;
    for j=0:NumGates-1
        temp=EC_add(temp,EC_pmult(Bp(i,j+1),sigma1_2(j+1)));
    end
    temp_Proof_B=EC_add(temp_Proof_B,EC_pmult(R(i),temp));
end
temp_Proof_B=EC_add(temp_Proof_B,EC_pmult(s,sigma1_1(3)));


Proof_C=EC_add(EC_pmult(s,Proof_A),EC_pmult(r,temp_Proof_B));
Proof_C=EC_add(Proof_C,EC_inv(EC_pmult(r,EC_pmult(s,sigma1_1(3)))));
for i=Ind_mid
    Proof_C=EC_add(Proof_C,EC_pmult(R(i),sigma1_4(i)));
end
for i=0:NumGates-2
    Proof_C=EC_add(Proof_C,EC_pmult(Hp(i+1),sigma1_5(i+1)));
end
proof=[Proof_A;Proof_B;Proof_C];
disp('Proof has made')

%% Debuging code: Check the completeness of proof
A=mod(alpha+R*Ax_val+r*delta,q);
B=mod(beta+R*Bx_val+s*delta,q);
C=mod(MODinv(delta,q)*(R(Ind_mid)*(beta*Ax_val(Ind_mid)+alpha*Bx_val(Ind_mid)+Cx_val(Ind_mid))+Hx_val*Zx_val)...
    +A*s+B*r+mod(-r*s*delta,q),q);

lhs=mod(A*B,q);
rhs=0;
rhs=mod(rhs+alpha*beta,q);
rhs=mod(rhs+gamma*R(Ind_IO)*VAL(Ind_IO).',q);
rhs=mod(rhs+C*delta,q);

proofcheckflag=1;
tempA=EC_pmult(A,g);
tempB=EC_pmult(B,h);
tempC=EC_pmult(C,g);
proofcheckflag=proofcheckflag*(tempA.x==Proof_A.x)*(tempA.y==Proof_A.y)...
    *(tempB.x==Proof_B.x)*(tempB.y==Proof_B.y)...
    *(tempC.x==Proof_C.x)*(tempC.y==Proof_C.y);
if lhs==rhs && proofcheckflag
    disp('Proof is complete')
else
    disp('Proof is incomplete')
end


%% Verify
% modular by p
% e=@(u,v) cmod(weil(EC_pmult(u,g),EC_pmult(v,h),Group1,Group2),p);
% e11=e(1,1);
% % e(A*g, B*h)
LHS=cmod(weil(proof(1),proof(2),Group1,Group2),p);
% testLHS=1;
% for i=1:lhs
%     testLHS=cmod(testLHS*e11,p);
% end
RHS=1;
% e(alpha*g, beta*h)
RHS=cmod(RHS*weil(sigma1_1(1),sigma2_1(1),Group1,Group2),p);
temp=PointInf1;
for i=Ind_IO
    temp=EC_add(temp,EC_pmult(R(i),sigma1_3(i)));
end
RHS=cmod(RHS*weil(temp,sigma2_1(2),Group1,Group2),p);
% for i=Ind_IO
% %   RHS=cmod(RHS*weil(EC_pmult(R(i),sigma1_3(i)),sigma2_1(2),Group1,Group2),q);
%     expon=cmod(weil(sigma1_3(i),h,Group1,Group2),p);
%     for j=1:R(i)
%         RHS=cmod(RHS*expon,p);
%     end
% %     RHS=cmod(RHS*weil(sigma1_3(i),sigma2_1(2),Group1,Group2)^R(i),q);
% end
% e(C*g, delta*h)
RHS=cmod(RHS*weil(proof(3),sigma2_1(3),Group1,Group2),p);
% testRHS=1;
% for i=1:rhs
%     testRHS=cmod(testRHS*e11,p);
% end
VfyResult=LHS==RHS;
if RHS==1 && LHS==1
    disp('Unable to verify, please retry')
elseif VfyResult==1
    disp('Verification Success')
else
    disp('Verification Failure')
end