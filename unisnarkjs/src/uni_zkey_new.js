import * as curves from "./curves.js"
import * as misc from 'misc.js'
import * as zkeyUtils from "./uni_zkey_utils.js";
import {
    readBinFile,
    createBinFile,
    readSection,
    writeBigInt,
    startWriteSection,
    endWriteSection,
} from "@iden3/binfileutils";

function createTauKey(curve, rng) {
    if (rng.length != 6) throw new Error('It should have six elements.')
    const key = {
        x: curve.Fr.fromRng(rng[0]),
        y: curve.Fr.fromRng(rng[1]),
        alpha_u: curve.Fr.fromRng(rng[2]),
        alpha_v: curve.Fr.fromRng(rng[3]),
        gamma_a: curve.Fr.fromRng(rng[4]),
        gamma_z: curve.Fr.fromRng(rng[5])
    }
    return key
}
export default async function uniSetup(curveName, n, s_max, r1csName, zkeyName, entropy) {
    
    const {fd: fdR1cs, sections: sectionsR1cs} = await readBinFile(r1csName, "r1cs", 1, 1<<22, 1<<24)
    const r1cs = await readR1csHeader(fdR1cs, sectionsR1cs, false)

    const fdZKey = await createBinFile(zkeyName, "zkey", 1, 10, 1<<22, 1<<24)

    const curve = await curves.getCurveFromName(curveName)
    const sG1 = curve.G1.F.n8*2
    const sG2 = curve.G2.F.n8*2
    const buffG1 = curve.G1.oneAffine;
    const buffG2 = curve.G2.oneAffine;
    const Fr = curve.Fr;
    const G1 = curve.G1;
    const G2 = curve.G2;

    if (r1cs.prime != curve.r) {
        throw new Error("r1cs curve does not match powers of tau ceremony curve")
        //return -1
    }

    const cirPower = log2(r1cs.nConstraints + r1cs.nPubInputs + r1cs.nOutputs +1 -1) +1
    const nPublic = r1cs.nOutputs + r1cs.nPubInputs;
    const domainSize = 2 ** cirPower;

    if (cirPower > power1) {
        throw new Error(`circuit too big for this power of tau ceremony. ${r1cs.nConstraints}*2 > 2**${power}`)
        //return -1
    }

    var num_keys = 6 // the number of keys from ptau
    let rng = new Array(num_keys)
    for(var i = 0; i < num_keys; i++) {
        rng[i] = await misc.getRandomRng(entropy + i)
    }

    const tau = createTauKey(curve, rng)

    // Write the header
    ///////////
    await startWriteSection(fdZKey, 1);
    await fdZKey.writeULE32(1); // Groth
    await endWriteSection(fdZKey);

    // Write the Groth header section
    ///////////

    await startWriteSection(fdZKey, 2);
    const primeQ = curve.q;
    const n8q = (Math.floor( (Scalar.bitLength(primeQ) - 1) / 64) +1)*8;

    const primeR = curve.r;
    const n8r = (Math.floor( (Scalar.bitLength(primeR) - 1) / 64) +1)*8;
    const Rr = Scalar.mod(Scalar.shl(1, n8r*8), primeR);
    const R2r = curve.Fr.e(Scalar.mod(Scalar.mul(Rr,Rr), primeR));

    await fdZKey.writeULE32(n8q);
    await writeBigInt(fdZKey, primeQ, n8q);
    await fdZKey.writeULE32(n8r);
    await writeBigInt(fdZKey, primeR, n8r);
    await fdZKey.writeULE32(r1cs.nVars);                         // Total number of bars
    await fdZKey.writeULE32(nPublic);                       // Total number of public vars (not including ONE)
    await fdZKey.writeULE32(domainSize);                  // domainSize
    await endWriteSection(fdZKey);

     // Write the sigma_G section
    ///////////

    await startWriteSection(fdZKey, 3);
    let vk_alpha_u1;
    vk_alpha_u1 = await G1.timesFr( buffG1, tau.alpha_u );
    let vk_alpha_v1;
    vk_alpha_v1 = await G1.timesFr( buffG1, tau.alpha_v );
    let vk_gamma_a1;
    vk_gamma_a1 = await G1.timesFr( buffG1, tau.gamma_a );

    await zkeyUtils.writeG1(fdZkey, curve, vk_alpha_u1);
    await zkeyUtils.writeG1(fdZkey, curve, vk_alpha_v1);
    await zkeyUtils.writeG1(fdZkey, curve, vk_gamma_a1);

    const x=tau.x;
    const y=tau.y;
    let vk_xy_pows;
    let xy_pows;
    for(var i = 0; i < n; i++) {
        for(var j=0; j<smax; j++){
            xy_pows= await Fr.mul(Fr.exp(x,Fr.e(i)),Fr.exp(y,Fr.e(j)));
            vk_xy_pows= await G1.timesFr( buffG1, xy_pows );
            await zkeyUtils.writeG1(fdZkey, curve, vk_xy_pows );
            // [x^0*y^0], [x^0*y^1], ..., [x^0*y^(s_max-1)], [x^1*y^0], ...
        }
    }

    const gamma_a_inv=Fr.inv(tau.gamma_a);
    let vk_xy_pows_t;
    let xy_pows_t;
    const t_xy=Fr.mul(Fr.sub(Fr.exp(x,n),Fr.one), Fr.sub(Fr.exp(y,s_max),Fr.one));
    const t_xy_g=Fr.mul(t_xy,gamma_a_inv);
    for(var i = 0; i < n-1; i++) {
        for(var j=0; j<smax-1; j++){
            xy_pows= await Fr.mul(Fr.exp(x,Fr.e(i)),Fr.exp(y,Fr.e(j)));
            xy_pows_t= await Fr.mul(xy_pows, t_xy_g);
            vk_xy_pows_t= await G1.timesFr( buffG1, xy_pows_t );
            await zkeyUtils.writeG1( fdZkey, curve, vk_xy_pows_t );
            // [x^0*y^0*t*g], [x^0*y^1*t*g], ..., [x^0*y^(s_max-1)*t*g], [x^1*y^0*t*g], ...
        }
    }
    await endWriteSection(fdZkey);

     // Write the sigma_H section
    ///////////

    await startWriteSection(fdZKey, 4);
    let vk_alpha_u2;
    vk_alpha_u2 = await G2.timesFr( buffG2, tau.alpha_u );
    let vk_gamma_z2;
    vk_gamma_z2 = await G2.timesFr( buffG2, tau.gamma_z );
    let vk_gamma_a2;
    vk_gamma_a2 = await G2.timesFr( buffG2, tau.gamma_a );
    await zkeyUtils.writeG2(fdZkey, curve, vk_alpha_u2);
    await zkeyUtils.writeG2(fdZkey, curve, vk_gamma_z2);
    await zkeyUtils.writeG2(fdZkey, curve, vk_gamma_a2);
    await endWriteSection(fdZkey);






}
