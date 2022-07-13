clear
code = text2code('opcodestring.txt');
codelen=length(code);
trash=randi(10,1,100)-1;
trash=num2str(trash);
trash=replace(trash,' ','');
environdata=cell(1,length(trash)/2);
for i=1:length(trash)/2
    environdata{i}=trash((i-1)*2+1:(i-1)*2+2);
end
environlen=length(environdata);
code=[code environdata];


%environment data pointers (hard coded)
Iv_pt=codelen+1;
lv_len=3;


%opcode classes
set_pushes=mat2cell(lower(dec2hex(96:127,2)),ones(1,32),2); %127-96+1=32
set_ariths=mat2cell(lower(dec2hex([1:11 16:29],2)),ones(1,25),2); %29-16+1 + 11-1+1 = 25


oplist=struct('opcode',[],'inputs',[],'outputs',[]);
stack_pt=[];
mem_pt={};
jump_map=[];
EoC_list=[]; %exit codes list
stack_pointer=1;
op_pointer=1;

pc=0;

while pc<codelen
    pc=pc+1;
    op=code{pc};
    
    disp(stack_pt)
    disp(mem_pt)
    disp(oplist)
    display(op)
    
    switch op
        case set_pushes   %pushes
            opnum=hex2dec(op);
            refnum=hex2dec('60');
            pushlen=opnum-refnum+1;
            stack_pt=[[0 pc+1 pushlen]; stack_pt];
            pc=pc+pushlen;
        case '52'   %mstore
            data=code2data(code,stack_pt(1,2),stack_pt(1,3));
            mem_pt=[[data stack_pt(2,:)];mem_pt];
            stack_pt=stack_pt(3:end,:);
        case '34'   %callvalue
            stack_pt=[[0 Iv_pt lv_len]; stack_pt];
        case '80'   %dup1
            stack_pt=[stack_pt(1,:); stack_pt];
        case set_ariths  %arithmetic operations
            switch op
                case {'15'}
                    d=1;
                    a=1;
            end
             
            op_pointer=op_pointer+1;
            oplist=wire_mapping(oplist, op, op_pointer,stack_pt, d, a);
            
            stack_pt=stack_pt(d+1:end,:); % remove d items from stack
            stack_pt=[oplist(op_pointer).outputs; stack_pt]; %add a items into stack
                    
        case '57' %jumpi
            d=34; % subcircuit has 34 inputs but instruction has 2 inputs: jump dest. and flag
            a=33; % subcircuit has 33 outputs but nothig is added to stack
            %output1=input2: flag in stack[1]
            %output2~17=input3~18: stack[2~17]
            %output18~33=input19~34: memory
            
            op_pointer=op_pointer+1;
            data=code2data(code,stack_pt(1,2),stack_pt(1,3));
            jumpdest=hex2dec(data);
            if stack_pt(1,1)~=0
                error('wrong jump dest')
            end
            jump_map=[jump_map;[op_pointer jumpdest]];
            stack_pt=stack_pt(2:end,:);
            
            stack_buffer=stack_pt;
            if size(stack_buffer,1)<d
                stack_buffer=[stack_buffer; zeros(d-size(stack_buffer,1),3)];
            end
            oplist=wire_mapping(oplist, op, op_pointer,stack_buffer, d, a);
            stack_pt=stack_pt(2:end,:);
            
        case 'fd' %revert
            d=2;
            a=33; %subcircuit has 33 outputs but nothig is added to stack
            %output1: flag stored in jumpi opcode pointed by jumpdest located at pc+1.
            %output2~33: memory data addressed from stack[0] to stack[0]+stack[1]-1
            %Assume: jumpdest is always next to revert.
            
            op_pointer=op_pointer+1;
            EoC_list=[EoC_list op_pointer];
            
            
            oplist¿Í stack¼öÁ¤
                      
            
            
            
            
            
            
            
            
        case {'01', '02', '03', '04', '05', '06', '07', '0a', '0b', '10', '11', '12', '13', '14', '16', '17', '18', '1a', '1b', '1c', '1d'}
            d=2;
            a=1;
            
    
        
    end
    
    
end

