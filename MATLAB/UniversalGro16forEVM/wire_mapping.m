function oplist_out=wire_mapping(oplist, op, op_pointer, stack_pt, d, a)
oplist(1).opcode='load';
for i=1:d
    if stack_pt(i,1)==0
        if isempty(oplist(1).outputs)
            checks=0;
        else
            checks=ismember(oplist(1).outputs,stack_pt(i,:),'rows');
        end
        if sum(checks)==0
            oplist(1).outputs=[oplist(1).outputs; stack_pt(i,:)];
            stack_pt(i,:)=[1 size(oplist(1).outputs,1) 1];
        else
            stack_pt(i,:)=[1 find(checks==1) 1];
        end
    end
end

oplist(op_pointer).opcode=op;
oplist(op_pointer).inputs=[oplist(op_pointer).inputs; stack_pt(1:d,:)];
oplist(op_pointer).outputs=[ones(a,1)*op_pointer (1:a).' ones(a,1)];
oplist_out=oplist;
end

