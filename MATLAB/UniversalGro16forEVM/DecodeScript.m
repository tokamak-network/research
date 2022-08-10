clear
clc
global oplist code set_pushes set_ariths set_dups set_swaps set_logs cjmplist ...
    environ_pts codewdata call_pt calldepth op_pointer cjmp_pointer ...
 set_normalhalt storage_pt callcode_suffix callcode_suffix_pt ...
 callresultlist call_pointer

code = text2code('opcodestring3.txt');
codelen=length(code);

%suffix callcode used to prove and verify the bool result of each CALL: (current)calldepth<1024 && value<=balance
callcode_suffix_raw='63fffffffd5447101561040163fffffffe541016'; % assuming storage addresses 'fffffffe' and 'ffffffff' are not used by EVM.
callcode_suffix_pt=codelen+1;
callcode_suffix_len=length(callcode_suffix_raw)/2;
callcode_suffix=mat2cell(callcode_suffix_raw,1,2*ones(1,callcode_suffix_len));

%environment data pointers (hard coded)
environ_pts=struct();
environ_pts.pc_pt=callcode_suffix_pt+callcode_suffix_len;
environ_pts.pc_len=4;
environ_pts.Iv_pt=environ_pts.pc_pt+environ_pts.pc_len; % transaction value, I_v
environ_pts.Iv_len=32;
environ_pts.Id_pt=environ_pts.Iv_pt+environ_pts.Iv_len; %input data I_d
environ_pts.Id_len=36;
environ_pts.Id_len_info_pt=environ_pts.Id_pt+environ_pts.Id_len;
environ_pts.Id_len_info_len=2;
environ_pts.Is_pt=environ_pts.Id_len_info_pt+environ_pts.Id_len_info_len;
environ_pts.Is_len=32;
environ_pts.od_pt=environ_pts.Is_pt+environ_pts.Is_len; %output data, o
environ_pts.od_len=32*4;
environ_pts.od_len_info_pt=environ_pts.od_pt+environ_pts.od_len;
environ_pts.od_len_info_len=1;
environ_pts.sd_pt=environ_pts.od_len_info_pt+environ_pts.od_len_info_len; %storage data
environ_pts.sd_len=32;
environ_pts.calldepth_pt=environ_pts.sd_pt+environ_pts.sd_len; %I_e
environ_pts.calldepth_len=2;
environ_pts.balance_pt=environ_pts.calldepth_pt+environ_pts.calldepth_len; % sigma[I_a]_b
environ_pts.balance_len=32;

%Arbitrary environment data
pcdata=replace(num2str(zeros(1,environ_pts.pc_len*2)),' ','');
Ivdata=replace(num2str(zeros(1,environ_pts.Iv_len*2)),' ','');
Ivdata(end)='0';
%Iddata=replace(num2str(zeros(1,Id_len*2)),' ','');
%Iddata(end-8+1:end)='a3dcb4d2';
Iddata='73ffd5b7000000000000000000000000000000000000000000000000000000000000000a';
Id_lendata=dec2hex(environ_pts.Id_len,environ_pts.Id_len_info_len*2);
%Isdata=replace(num2str(zeros(1,Is_len*2)),' ','');
Isdata='000000000000000000000000617f2e2fd72fd9d5503197092ac168c91465e7f2';
oddata=replace(num2str(zeros(1,environ_pts.od_len*2)),' ','');
od_lendata=dec2hex(environ_pts.od_len,environ_pts.od_len_info_len*2);
sddata=replace(num2str(zeros(1,environ_pts.sd_len*2)),' ','');
sddata(end-1:end)='55';
calldepthdata=replace(num2str(zeros(1,environ_pts.calldepth_len*2)),' ','');
balancedata=dec2hex(10^6, environ_pts.balance_len*2);

data=strcat(pcdata,Ivdata,Iddata,Id_lendata,Isdata,oddata,od_lendata,sddata, ...
    calldepthdata, balancedata);
environdata=mat2cell(data,1,2*ones(1,length(data)/2));
environlen=length(environdata);
codewdata=[code callcode_suffix environdata];


%opcode classes
set_pushes=mat2cell(lower(dec2hex(96:127,2)),ones(1,32),2); %127-96+1=32
set_ariths=mat2cell(lower(dec2hex([1:11 16:29],2)),ones(1,25),2); %29-16+1 + 11-1+1 = 25
set_dups=mat2cell(lower(dec2hex(128:143,2)),ones(1,16),2); %143-128+1=16
set_swaps=mat2cell(lower(dec2hex(144:159,2)),ones(1,16),2); %159-144+1=16
set_logs=mat2cell(lower(dec2hex(160:164,2)),ones(1,5),2); %164-160+1=5
set_normalhalt={'00', 'f3', 'fd', 'ff'};


oplist=struct('opcode',[],'pt_inputs',[],'pt_outputs',[], 'inputs', [], 'outputs',[]);
op_pointer=1;
cjmplist=struct('pc',[],'pt_inputs',[],'condition',[],'destination',[]);
cjmp_pointer=0;
storage_pt=containers.Map('KeyType','uint32','ValueType','any'); %valuetype = [op_pointer pt length]
call_pt=[]; %[ROM_offset call_code_length]
calldepth=0;
callresultlist=[]; %op_pointers
call_pointer=0;




%Decode starts
calldepth=calldepth+1;
codewdata(environ_pts.calldepth_pt:environ_pts.calldepth_pt+environ_pts.calldepth_len-1)= ...
    mat2cell(dec2hex(calldepth,environ_pts.calldepth_len*2),1,2*ones(1,environ_pts.calldepth_len));
% curr_calldepth=hex2dec(cell2mat(codewdata(environ_pts.calldepth_pt:environ_pts.calldepth_pt+environ_pts.calldepth_len-1)));
call_pt(calldepth,:)=[1 codelen];
outputs_pt=Decode(code);
oplist(1).pt_inputs=[oplist(1).pt_inputs;outputs_pt];
%%%% decode end %%%%

s_F=length(oplist);
%Find input and output values
for k=1:s_F
    k_pt_inputs=oplist(k).pt_inputs;
    k_inputs=[];
    for i=1:size(k_pt_inputs,1)
        k_inputs=[k_inputs; eval_EVM(k_pt_inputs(i,:))];
    end
    
    k_pt_outputs=oplist(k).pt_outputs;
    k_outputs=[];
    for i=1:size(k_pt_outputs,1)
        k_outputs=[k_outputs; eval_EVM(k_pt_outputs(i,:))];
    end
    oplist(k).inputs=k_inputs;
    oplist(k).outputs=k_outputs;
end

%Make wireMap
Instruction_Wire_Numbers=jsondecode(fileread('wireList.json'));
Con_Instruction_Wire_Numbers=containers.Map('KeyType','uint32','ValueType','any');
Con_Instruction_Idx=containers.Map('KeyType','uint32','ValueType','any');
s_D=length(Instruction_Wire_Numbers);
for k=1:s_D
    Con_Instruction_Wire_Numbers(hex2dec(Instruction_Wire_Numbers(k).opcode(3:end)))=Instruction_Wire_Numbers(k).Nwires;
    Con_Instruction_Idx(hex2dec(Instruction_Wire_Numbers(k).opcode(3:end)))=k-1;
end
NWires=zeros(1,s_F);
for k=1:s_F
    if strcmp(oplist(k).opcode, 'fff')
        NWires(k)=32;
    else
        NWires(k)=Con_Instruction_Wire_Numbers(hex2dec(oplist(k).opcode));
    end
end
CoDomain_Len=sum(NWires);

% Initialize RangeCell
RangeCell=cell(s_F,max(NWires));
NZEROWIRES=1;
NINPUT=32;
for i=1:NINPUT*2
    RangeCell{1,i}=[RangeCell{1,i} [1 mod((i-1),32)+1]];
end
for k=2:s_F
    RangeCell{1,1}=[RangeCell{1,1}; [k 1]];
end
for k=2:s_F
    oplist_k=oplist(k);
    k_pt_inputs=oplist_k.pt_inputs;
    inlen=size(oplist_k.pt_inputs, 1);
    outlen=size(oplist_k.pt_outputs, 1);
    NWires_k=NWires(k);
    for j=1:NWires_k
        if (j>NZEROWIRES && j<=NZEROWIRES+outlen) || (j>NZEROWIRES+outlen+inlen)
            RangeCell{k,j}=[RangeCell{k,j}; [k,j]];
        end
    end
end
% Apply oplist into RangeCell
for k=2:s_F
    oplist_k=oplist(k);
    k_pt_inputs=oplist_k.pt_inputs;
    inlen=size(oplist_k.pt_inputs, 1);
    outlen=size(oplist_k.pt_outputs, 1);
    NWires_k=NWires(k);
    for i=1:inlen
        RangeCell{k_pt_inputs(i,1), NZEROWIRES+k_pt_inputs(i,2)}= ...
        [RangeCell{k_pt_inputs(i,1), NZEROWIRES+k_pt_inputs(i,2)}; [k,NZEROWIRES+outlen+i]];
    end
end

WireListm=[];
for k=1:s_F
    NWires_k=NWires(k);
    for i=1:NWires_k
        if ~isempty(RangeCell{k,i})
            WireListm=[WireListm; [k-1, i-1]];
        end
    end
end
mWires=size(WireListm,1);

OpLists=zeros(1,s_F);
for k=1:s_F
    OpLists(k)=Con_Instruction_Idx(hex2dec(oplist(k).opcode));
end

% Following definition (applicable when CJUMP is implemented)
% I_V=[];
% I_P=[];
% for i=1:mWires
%     k=WireListm(i,1)+1;
%     wireIdx=WireListm(i,2)+1;
%     oplist_k=oplist(k);
%     if k==0
%         inlen=NINPUT;
%         outlen=NINPUT;
%     else 
%         inlen=size(oplist_k.pt_inputs, 1);
%         outlen=size(oplist_k.pt_outputs, 1);
%     end
%     if size(RangeCell{k,wireIdx},1)>1
%         I_V=[I_V i-1];
%     elseif size(RangeCell{k,wireIdx},1)==1
%         I_P=[I_P i-1];
%     else
%         error('error')
%     end
% end

% Temporary construnction berfore implementing CJUMP
I_V=[];
I_P=[];
for i=1:mWires
    k=WireListm(i,1);
    wireIdx=WireListm(i,2);
    oplist_k=oplist(k+1);
    if k==0
        inlen=NINPUT;
        outlen=NINPUT;
    else 
        inlen=size(oplist_k.pt_inputs, 1);
        outlen=size(oplist_k.pt_outputs, 1);
    end
    if wireIdx>=NZEROWIRES && wireIdx<NZEROWIRES+outlen
        I_V=[I_V i-1];
    else
        I_P=[I_P i-1];
    end
end

I_V_len=length(I_V);
I_P_len=length(I_P);
rowInv_I_V=[];
rowInv_I_P=[];
for i=I_V+1
    k=WireListm(i,1);
    wireIdx=WireListm(i,2);
    InvSet=RangeCell{k+1,wireIdx+1}-1;
    NInvSet=size(InvSet,1);
    InvSet=reshape(InvSet.',NInvSet*2,1).';
    rowInv_I_V=[rowInv_I_V NInvSet InvSet];
end
for i=I_P+1
    k=WireListm(i,1);
    wireIdx=WireListm(i,2);
    InvSet=RangeCell{k+1,wireIdx+1}-1;
    NInvSet=size(InvSet,1);
    InvSet=reshape(InvSet.',NInvSet*2,1).';
    rowInv_I_P=[rowInv_I_P NInvSet InvSet];
end
% set_i_v.bin format with data_size=2 bytes:
% [data_size(4) I_V_len(2) I_V(2*I_V_len) NPreImages_I_V_1(2) ...
% PreImages_I_V_1(2*2*NPreImages_I_V_1) NPreImages_I_V_2(2) ...
% PreImages_I_V_2(2*2*NPreImages_I_V_2) ...],
% where PreImages = [k1, i1, k2, i2, k3, i3, ...]

SetData_I_V=[0 2 I_V_len I_V rowInv_I_V];
SetData_I_P=[0 2 I_P_len I_P rowInv_I_P];
fdset1=fopen('Set_I_V.bin', 'w');
fdset2=fopen('Set_I_P.bin', 'w');
fwrite(fdset1, SetData_I_V, 'uint16');
fwrite(fdset2, SetData_I_P, 'uint16');
fclose(fdset1);
fclose(fdset2);



