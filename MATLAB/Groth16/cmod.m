function [ out ] = cmod( val,q )
%UNTITLED8 Summary of this function goes here
%   Detailed explanation goes here
if real(val)*imag(val)==inf || real(val)*imag(val)==-inf
    display('Warn: modular of inf or -inf')
    out=val;
else
    out=mod(real(val),q)+mod(imag(val),q)*sqrt(-1);
end

end

