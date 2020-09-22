function [ ind ] = findfactor( target,factor )
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here

ind=0;
for i=1:length(target)
    div=target(i)/factor;
    if length(symvar(div))==0
        ind=i;
        break;
    end
%     if isequal(target(i),factor)
%         ind=i;
%         break;
%     end
end


end

