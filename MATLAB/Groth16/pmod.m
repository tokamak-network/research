function [ polyout ] = pmod( poly,q )
% Take modular on coefficients of symbolic polynomials

[c,t]=coeffs(poly);
c=rmod(c,q);
polyout=c*t.';
end

