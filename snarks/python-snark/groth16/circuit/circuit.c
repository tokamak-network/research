#include "circom.hpp"
#include "calcwit.hpp"
#define NSignals 1004
#define NComponents 1
#define NOutputs 1
#define NInputs 2
#define NVars 1003
#define __P__ "21888242871839275222246405745257275088548364400416034343698204186575808495617"

/*
Multiplier
n=1000
*/
void Multiplier_e56df795f320fbb8(Circom_CalcWit *ctx, int __cIdx) {
    FrElement _sigValue[1];
    FrElement _sigValue_1[1];
    FrElement _tmp[1];
    FrElement _sigValue_2[1];
    FrElement _tmp_1[1];
    FrElement _sigValue_3[1];
    FrElement _sigValue_4[1];
    FrElement _tmp_5[1];
    FrElement _sigValue_5[1];
    FrElement _tmp_6[1];
    FrElement _tmp_8[1];
    FrElement i[1];
    FrElement _tmp_9[1];
    FrElement _sigValue_6[1];
    FrElement _tmp_10[1];
    FrElement _sigValue_7[1];
    FrElement _tmp_11[1];
    FrElement _sigValue_8[1];
    FrElement _tmp_12[1];
    FrElement _tmp_13[1];
    FrElement _tmp_14[1];
    FrElement _sigValue_9[1];
    int _a_sigIdx_;
    int _b_sigIdx_;
    int _int_sigIdx_;
    int _offset;
    int _offset_5;
    int _offset_7;
    int _offset_9;
    int _offset_15;
    int _offset_17;
    int _offset_19;
    int _offset_25;
    int _c_sigIdx_;
    Circom_Sizes _sigSizes_int;
    PFrElement _loopCond;
    Fr_copy(&(_tmp_8[0]), ctx->circuit->constants +1);
    Fr_copy(&(i[0]), ctx->circuit->constants +2);
    _a_sigIdx_ = ctx->getSignalOffset(__cIdx, 0xaf63dc4c8601ec8cLL /* a */);
    _b_sigIdx_ = ctx->getSignalOffset(__cIdx, 0xaf63df4c8601f1a5LL /* b */);
    _int_sigIdx_ = ctx->getSignalOffset(__cIdx, 0x2b9fff192bd4c83eLL /* int */);
    _c_sigIdx_ = ctx->getSignalOffset(__cIdx, 0xaf63de4c8601eff2LL /* c */);
    _sigSizes_int = ctx->getSignalSizes(__cIdx, 0x2b9fff192bd4c83eLL /* int */);
    /* signal private input a */
    /* signal private input b */
    /* signal output c */
    /* signal int[n] */
    /* int[0] <== a*a + b */
    ctx->getSignal(__cIdx, __cIdx, _a_sigIdx_, _sigValue);
    ctx->getSignal(__cIdx, __cIdx, _a_sigIdx_, _sigValue_1);
    Fr_mul(_tmp, _sigValue, _sigValue_1);
    ctx->getSignal(__cIdx, __cIdx, _b_sigIdx_, _sigValue_2);
    Fr_add(_tmp_1, _tmp, _sigValue_2);
    _offset = _int_sigIdx_;
    ctx->setSignal(__cIdx, __cIdx, _offset, _tmp_1);
    /* for (var i=1;i<n;i++) */
    /* int[i] <== int[i-1]*int[i-1] + b */
    _offset_5 = _int_sigIdx_;
    ctx->getSignal(__cIdx, __cIdx, _offset_5, _sigValue_3);
    _offset_7 = _int_sigIdx_;
    ctx->getSignal(__cIdx, __cIdx, _offset_7, _sigValue_4);
    Fr_mul(_tmp_5, _sigValue_3, _sigValue_4);
    ctx->getSignal(__cIdx, __cIdx, _b_sigIdx_, _sigValue_5);
    Fr_add(_tmp_6, _tmp_5, _sigValue_5);
    _offset_9 = _int_sigIdx_ + 1*_sigSizes_int[1];
    ctx->setSignal(__cIdx, __cIdx, _offset_9, _tmp_6);
    _loopCond = _tmp_8;
    while (Fr_isTrue(_loopCond)) {
        /* int[i] <== int[i-1]*int[i-1] + b */
        Fr_sub(_tmp_9, i, (ctx->circuit->constants + 1));
        _offset_15 = _int_sigIdx_ + Fr_toInt(_tmp_9)*_sigSizes_int[1];
        ctx->getSignal(__cIdx, __cIdx, _offset_15, _sigValue_6);
        Fr_sub(_tmp_10, i, (ctx->circuit->constants + 1));
        _offset_17 = _int_sigIdx_ + Fr_toInt(_tmp_10)*_sigSizes_int[1];
        ctx->getSignal(__cIdx, __cIdx, _offset_17, _sigValue_7);
        Fr_mul(_tmp_11, _sigValue_6, _sigValue_7);
        ctx->getSignal(__cIdx, __cIdx, _b_sigIdx_, _sigValue_8);
        Fr_add(_tmp_12, _tmp_11, _sigValue_8);
        _offset_19 = _int_sigIdx_ + Fr_toInt(i)*_sigSizes_int[1];
        ctx->setSignal(__cIdx, __cIdx, _offset_19, _tmp_12);
        Fr_add(_tmp_13, i, (ctx->circuit->constants + 1));
        Fr_copyn(i, _tmp_13, 1);
        Fr_lt(_tmp_14, i, (ctx->circuit->constants + 3));
        _loopCond = _tmp_14;
    }
    /* c <== int[n-1] */
    _offset_25 = _int_sigIdx_ + 999*_sigSizes_int[1];
    ctx->getSignal(__cIdx, __cIdx, _offset_25, _sigValue_9);
    ctx->setSignal(__cIdx, __cIdx, _c_sigIdx_, _sigValue_9);
    ctx->finished(__cIdx);
}
// Function Table
Circom_ComponentFunction _functionTable[1] = {
     Multiplier_e56df795f320fbb8
};
