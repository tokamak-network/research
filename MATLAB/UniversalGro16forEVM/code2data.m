function hexdata=code2data(code,pointer,length)
    hexdata=cell2mat(code(pointer:pointer+length-1));
    hexdata={hexdata};
end

