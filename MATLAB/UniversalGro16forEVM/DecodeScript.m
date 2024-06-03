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


oplist=struct('opcode',[],'pt_inputs',[],'pt_outputs',[],'outputs',[]);
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

