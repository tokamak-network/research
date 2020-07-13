function [ tf ] = Peq( Point1, Point2 )
%UNTITLED12 Summary of this function goes here
%   Detailed explanation goes here
% if Point1.k~=Point2.k
%     error('mismatched degree')
% end
if Point1.k==Point2.k && Point1.x==Point2.x && Point1.y==Point2.y
    tf=1;
else
    tf=0;
end

end

