import * as curves from "./curves.js"
import * as misc from './misc.js'
import * as zkeyUtils from "./uni_zkey_utils.js";
import BigArray from "./bigarray.js";
import chai from "chai";
const assert = chai.assert
import {readR1csHeader} from "r1csfile";
import {
    readBinFile,
    readSection,
    createBinFile,
    writeBigInt,
    readBigInt,
    startWriteSection,
    endWriteSection,
    startReadUniqueSection,
    endReadSection
} from "@iden3/binfileutils";
import { Scalar, F1Field, getCurveFromR} from "ffjavascript";
import fs from "fs"
import * as fastFile from "fastfile"
import { O_TRUNC, O_CREAT, O_RDWR, O_RDONLY} from "constants";



export default async function uni_Setup(curveName, s_D, min_s_max, r1csName, RSName, entropy) {
    const TESTFLAG = false;
    const r1cs = new Array();
    const sR1cs = new Array();
     
    for(var i=0; i<s_D; i++){
        let r1csIdx = String(i);
        const {fd: fdR1cs, sections: sectionsR1cs} = await readBinFile('resource/'+r1csName+r1csIdx+".r1cs", "r1cs", 1, 1<<22, 1<<24);
        r1cs.push(await readR1csHeader(fdR1cs, sectionsR1cs, false));
        sR1cs.push(await readSection(fdR1cs, sectionsR1cs, 2));
        await fdR1cs.close();
        // if(max_constraints == undefined){
        //     max_constraints = r1cs[i].nConstraints;
        // } else {
        //     if(r1cs[i].nConstraints>max_constraints){
        //         max_constraints = r1cs[i].nConstraints;
        //     }
        // }
    }
    const fdRS = await createBinFile('resource/'+RSName+".urs", "zkey", 1, 4+s_D, 1<<22, 1<<24);
    
    
    // //fdRS.fd.write(new Array())
    // //const fdRS = await fs.promises.open(RSName+".urs", O_TRUNC|O_CREAT|O_RDWR)
    // const buff = new Uint8Array(4);
    // for (let i=0; i<4; i++) buff[i] = "zkey".charCodeAt(i);
    // await fdRS.fd.write(buff, 0); // Magic "r1cs"
    // let tmpBuff32 = new Uint8Array(4);
    // let tmpBuff32v = new DataView(tmpBuff32.buffer);
    // tmpBuff32v.setUint32(0, 1, true);
    // await fdRS.fd.write(tmpBuff32);
    // tmpBuff32v.setUint32(0, 32, true);
    // await fdRS.fd.write(tmpBuff32);
    // fdRS.close()
    
    // const fdRSr = await fs.promises.open(RSName+".urs", O_RDONLY)

    // const b1 =new Uint8Array(4);
    // await fdRSr.read(b1,0,4,4);
    // const b2 =new Uint8Array(4);
    // await fdRSr.read(b2,0,4);
    // console.log(fdRSr.fd)
    // const b3 =new Uint8Array(4);
    // await fdRSr.read(b3,0,4);
    // console.log(fdRSr.fd)
    
    // const b1v = new DataView(b1.buffer);
    // const b2v = new DataView(b2.buffer);
    // const b3v = new DataView(b3.buffer);
    // console.log(b1v.getUint32(0, true));
    // console.log(b2.buffer);
    // console.log(b2v.getUint32(0, true));
    // console.log(b3.buffer);
    // console.log(b3v.getUint32(0, true));
    
    
    console.log('checkpoint0')

   

    //const fdRS = await fastFile.createOverride(RSName+".urs", 1<<22, 1<<24);
    //const fdRS =await fs.promises.open(RSName+".urs",  O_TRUNC | O_CREAT | O_RDWR);

    //await fdRS.writeULE32(1); // Version
    //await fdRS.writeULE32(4+s_D); // Number of Sections

    // const {fd: fdR1cs, sections: sectionsR1cs} = await readBinFile(r1csName+"0"+".r1cs", "r1cs", 1, 1<<22, 1<<24);
    // // await startReadUniqueSection(fdR1cs, sectionsR1cs, 1)
    // // let temp = await fdR1cs.readULE32();
    // // await readBigInt(fdR1cs, temp);
    // // await endReadSection(fdR1cs,1)
    // const r1cs = await readR1csHeader(fdR1cs, sectionsR1cs);
    // const fdZKey = await createBinFile(RSName, "zkey", 1, 9, 1<<22, 1<<24); // (fileName, type, version, nSections, cacheSize, pageSize)
    
    // let tmpBuff32 = new Uint8Array(4);
    // let tmpBuff32v = new DataView(tmpBuff32.buffer);
    // tmpBuff32v.setUint32(0, 255, true);
    // await fdZKey.fd.write(tmpBuff32);

    

      
    const curve = await curves.getCurveFromName(curveName);
    // const sG1 = curve.G1.F.n8*2              // unused
    // const sG2 = curve.G2.F.n8*2              // unused
    const buffG1 = curve.G1.oneAffine;
    const buffG2 = curve.G2.oneAffine;
    const Fr = curve.Fr;
    const G1 = curve.G1;
    const G2 = curve.G2;
    const NZeroWires = 1;


    
    if (r1cs[0].prime != curve.r) {
        console.log('checkpoint1');
        console.log("r1cs_prime: ", r1cs[0].prime);
        console.log("curve_r: ", curve.r);
        throw new Error("r1cs curve does not match powers of tau ceremony curve")
        //return -1
    }

    // const cirPower = log2(r1cs.nConstraints + r1cs.nPubInputs + r1cs.nOutputs +1 -1) +1
    // const domainSize = 2 ** cirPower;


    // Generate tau
    var num_keys = 6 // the number of keys in tau
    let rng = new Array(num_keys)
    for(var i = 0; i < num_keys; i++) {
        rng[i] = await misc.getRandomRng(entropy + i)
    }    
    const tau = createTauKey(Fr, rng)
    console.log(`checkpoint2`)

    // Write Header
    ///////////
    await startWriteSection(fdRS, 1);
    await fdRS.writeULE32(1); // Groth
    await endWriteSection(fdRS);
    // End of the Header
    console.log(`checkpoint3`)

    // Write parameters section
    ///////////
    await startWriteSection(fdRS, 2);
    const primeQ = curve.q;
    const n8q = (Math.floor( (Scalar.bitLength(primeQ) - 1) / 64) +1)*8;
    console.log(`checkpoint4`)

    // Group parameters
    const primeR = curve.r;
    const n8r = (Math.floor( (Scalar.bitLength(primeR) - 1) / 64) +1)*8;
    const Rr = Scalar.mod(Scalar.shl(1, n8r*8), primeR);
    const R2r = curve.Fr.e(Scalar.mod(Scalar.mul(Rr,Rr), primeR));

    await fdRS.writeULE32(n8q);                   // byte length of primeQ
    await writeBigInt(fdRS, primeQ, n8q);
    await fdRS.writeULE32(n8r);                   // byte length of primeR
    await writeBigInt(fdRS, primeR, n8r);

    // Instruction set constants
    await fdRS.writeULE32(s_D)
    const m = new Array()          // the numbers of wires
    const mPublic = new Array()    // the numbers of public wires (not including constant wire at zero index)
    const mPrivate = new Array()
    for(var i=0; i<s_D; i++){
        m.push(r1cs[i].nVars);
        mPublic.push(r1cs[i].nOutputs + r1cs[i].nPubInputs + r1cs[i].nPrvInputs) 
        mPrivate.push(m[i] - mPublic[i])
        await fdRS.writeULE32(m[i])
        await fdRS.writeULE32(mPublic[i])
    }

    // QAP constants
    const sum_mPublic = mPublic.reduce((accu,curr) => accu + curr)
    const sum_mPrivate = mPrivate.reduce((accu,curr) => accu + curr)
    const NEqs = Math.max(sum_mPublic, sum_mPrivate)
    let n = BigInt(Math.ceil(NEqs/3))

    let q_x = (primeR - BigInt(1)) / n
    while ((primeR - BigInt(1)) !== q_x * n){
        n += BigInt(1)
        q_x = (primeR - BigInt(1)) / n
    }

    console.log('n: ', n)

    const exp_omega_x = q_x
    let AnyNumber = n
    let omega_x = await Fr.exp(Fr.e(AnyNumber), exp_omega_x)
    while(Fr.toObject(omega_x) == 1){
        AnyNumber += BigInt(1)
        omega_x = await Fr.exp(Fr.e(AnyNumber), exp_omega_x)
    }

    
    let s_max = BigInt(min_s_max)
    let q_y = (primeR - BigInt(1)) / s_max
    while ((primeR - BigInt(1)) !== s_max * q_y){
        s_max += BigInt(1)
        q_y = (primeR - BigInt(1)) / s_max
    }
    const exp_omega_y = q_y 
    let omega_y = await Fr.exp(Fr.e(AnyNumber), exp_omega_y)
    while(Fr.toObject(omega_y) == 1){
        AnyNumber += BigInt(1)
        omega_y = await Fr.exp(Fr.e(AnyNumber), exp_omega_y)
    }
    
    console.log('s_max: ', s_max)

    // Test code 1 // --> DONE
    if(TESTFLAG){
        console.log(`Running Test 1`)
        assert(Fr.eq(await Fr.exp(Fr.e(n), primeR), Fr.e(n)))
        assert(Fr.eq(await Fr.exp(Fr.e(omega_x), n), Fr.one))
        assert(Fr.eq(await Fr.exp(Fr.e(omega_y), s_max), Fr.one))
        console.log(`Test 1 finished`)
    }
    // End of test code 1 //

    //const n8n = (Math.floor( (Scalar.bitLength(n) - 1) / 64) +1)*8;
    //await fdRS.writeULE32(n8n);                     // byte length of n
    //await writeBigInt(fdRS, n, n8n);                
    n = Number(n)
    s_max = Number(s_max)
    await fdRS.writeULE32(n);                       // the maximum number of gates in each subcircuit: n>=NEqs/3 and n|(r-1)
    await fdRS.writeULE32(s_max);                  // the maximum number of subcircuits in a p-code: s_max>min_s_max and s_max|(r-1)
    await writeBigInt(fdRS, Fr.toObject(omega_x), n8r);                    // Generator for evaluation points on X
    await writeBigInt(fdRS, Fr.toObject(omega_y), n8r);             // Generator for evaluation points on Y
    console.log(`checkpoint5`)

    // Test code 2 //
    if(TESTFLAG){
        console.log(`Running Test 2`)
        assert(Fr.eq(omega_x, Fr.e(Fr.toObject(omega_x))))
        console.log(`Test 2 finished`)
    }
    // End of test code 2 //

    await endWriteSection(fdRS);
    // End of the parameters section

    // Write the sigma_G section
    ///////////
    await startWriteSection(fdRS, 3);
    let vk1_alpha_u;
    vk1_alpha_u = await G1.timesFr( buffG1, tau.alpha_u );
    let vk1_alpha_v;
    vk1_alpha_v = await G1.timesFr( buffG1, tau.alpha_v );
    let vk1_gamma_a;
    vk1_gamma_a = await G1.timesFr( buffG1, tau.gamma_a );

    await zkeyUtils.writeG1(fdRS, curve, vk1_alpha_u);
    await zkeyUtils.writeG1(fdRS, curve, vk1_alpha_v);
    await zkeyUtils.writeG1(fdRS, curve, vk1_gamma_a);
    let x=tau.x;
    let y=tau.y;
    // if(TESTFLAG){  // UNUSED, since pairingEQ doesnt work for the points of infinity
    //     x=Fr.exp(omega_x, Fr.toObject(tau.x));
    //     y=Fr.exp(omega_y, Fr.toObject(tau.y));
    // }
    
    let vk1_xy_pows = Array.from(Array(n), () => new Array(s_max));
    let xy_pows = Array.from(Array(n), () => new Array(s_max)); // n by s_max 2d array

    for(var i = 0; i < n; i++) {
        for(var j = 0; j < s_max; j++){
            xy_pows[i][j] = await Fr.mul(await Fr.exp(x,i), await Fr.exp(y,j));
            vk1_xy_pows[i][j] = await G1.timesFr(buffG1, xy_pows[i][j]);
            await zkeyUtils.writeG1(fdRS, curve, vk1_xy_pows[i][j]);
            // [x^0*y^0], [x^0*y^1], ..., [x^0*y^(s_max-1)], [x^1*y^0], ...
        }
    }

    const gamma_a_inv=Fr.inv(tau.gamma_a);
    let xy_pows_tg;
    let vk1_xy_pows_tg = Array.from(Array(n-1), () => new Array(s_max-1));
    const t_xy=Fr.mul(Fr.sub(await Fr.exp(x,n),Fr.one), Fr.sub(await Fr.exp(y,s_max),Fr.one));
    const t_xy_g=Fr.mul(t_xy, gamma_a_inv);
    for(var i = 0; i < n-1; i++) {
        for(var j=0; j<s_max-1; j++){
            xy_pows_tg= await Fr.mul(xy_pows[i][j], t_xy_g);
            vk1_xy_pows_tg[i][j]= await G1.timesFr( buffG1, xy_pows_tg );
            await zkeyUtils.writeG1( fdRS, curve, vk1_xy_pows_tg[i][j] );
            // [x^0*y^0*t*g], [x^0*y^1*t*g], ..., [x^0*y^(s_max-1)*t*g], [x^1*y^0*t*g], ...
        }
    }
    await endWriteSection(fdRS);
    // End of the sigma_G section
    ///////////

     // Write the sigma_H section
    ///////////
    await startWriteSection(fdRS, 4);
    let vk2_alpha_u;
    vk2_alpha_u = await G2.timesFr( buffG2, tau.alpha_u );
    let vk2_gamma_z;
    vk2_gamma_z = await G2.timesFr( buffG2, tau.gamma_z );
    let vk2_gamma_a;
    vk2_gamma_a = await G2.timesFr( buffG2, tau.gamma_a );
    await zkeyUtils.writeG2(fdRS, curve, vk2_alpha_u);
    await zkeyUtils.writeG2(fdRS, curve, vk2_gamma_z);
    await zkeyUtils.writeG2(fdRS, curve, vk2_gamma_a);

    let vk2_xy_pows
    for(var i = 0; i < n; i++) {
        for(var j=0; j<s_max; j++){
            vk2_xy_pows= await G2.timesFr( buffG2, xy_pows[i][j] );
            await zkeyUtils.writeG2(fdRS, curve, vk2_xy_pows );
            // [x^0*y^0], [x^0*y^1], ..., [x^0*y^(s_max-1)], [x^1*y^0], ...
        }
    }
    await endWriteSection(fdRS);
    // End of the sigma_H section
    ///////////

    // Test code 3// --> DONE
    // To test [x^i*y^j*t(x,y)/gamma_a]_G in sigma_G
    // with e(A,B) == e(C,D), where
    // A = [x^i*y^j]_G in sigma_G,
    // B = t(x,y)*H
    // C is the target,
    // D = [gamma_a]_H in sigma_H
    if(TESTFLAG){
        console.log(`Running Test 3`)
        let vk2_t_xy =  await G2.timesFr(buffG2, t_xy)
        for (let i = 0; i < n - 1; i++) {
			for (let j = 0; j < s_max - 1; j++) {
                let res = await curve.pairingEq(
                    vk1_xy_pows[i][j],
                    vk2_t_xy, 
                    vk1_xy_pows_tg[i][j],
                     await G2.neg(vk2_gamma_a))
				assert(res)
			}
		}
        console.log(`Test 3 finished`)
    }
    // End of the test code 3//

    // Write the theta_G[i] sections for i in [0, 1, ..., s_D] (alpha*u(X)+beta*v(X)+w(X))/gamma
    ///////////
    let Lagrange_basis = new Array(n);
    let term
    let acc
    let multiplier
    for(var i=0; i<n; i++){
        term=Fr.one;
        acc=Fr.one;
        multiplier=Fr.mul(await Fr.exp(Fr.inv(omega_x),i),x);
        for(var j=1; j<n; j++){
            term=Fr.mul(term,multiplier);
            acc=Fr.add(acc,term);
        }
        Lagrange_basis[i]=Fr.mul(Fr.inv(Fr.e(n)),acc);
    }
    // let temp = new Array(n)
    // for(var i=0; i<n; i++){
    //     temp[i] = Fr.toObject(Lagrange_basis[i])
    // }
    // console.log('Lags ', temp)
    console.log(`checkpoint6`)

    for(var k = 0; k < s_D; k++){
               
        let processResults_k
        processResults_k = await processConstraints(); // to fill U, V, W
        let U = processResults_k.U
        let Uid = processResults_k.Uid
        let V = processResults_k.V
        let Vid = processResults_k.Vid
        let W = processResults_k.W
        let Wid = processResults_k.Wid
        console.log(`checkpoint7`)
    
        let ux = new Array(m[k]);
        let vx = new Array(m[k]);
        let wx = new Array(m[k]);
        for(var i=0; i<m[k]; i++){
            ux[i]=Fr.e(0);
            vx[i]=Fr.e(0);
            wx[i]=Fr.e(0);
        }
   
        let U_ids
        let U_coefs
        let V_ids
        let V_coefs
        let W_ids
        let W_coefs
        let Lagrange_term
        let U_idx
        let V_idx
        let W_idx
    
        for(var i=0; i<r1cs[k].nConstraints; i++){
            U_ids=Uid[i];
            U_coefs=U[i];
            V_ids=Vid[i];
            V_coefs=V[i];
            W_ids=Wid[i];
            W_coefs=W[i];
            for(var j=0; j<U_ids.length; j++){
                U_idx=U_ids[j]
                if(U_idx>=0){
                    Lagrange_term=Fr.mul(U_coefs[j],Lagrange_basis[i]);
                    ux[U_idx]=Fr.add(ux[U_idx],Lagrange_term);
                }
            }
            for(var j=0; j<V_ids.length; j++){
                V_idx=V_ids[j]
                if(V_idx>=0){
                    Lagrange_term=Fr.mul(V_coefs[j],Lagrange_basis[i]);
                    vx[V_idx]=Fr.add(vx[V_idx],Lagrange_term);
                }
            }
            for(var j=0; j<W_ids.length; j++){
                W_idx=W_ids[j]
                if(W_idx>=0){
                    Lagrange_term=Fr.mul(W_coefs[j],Lagrange_basis[i]);
                    wx[W_idx]=Fr.add(wx[W_idx],Lagrange_term);
                }
            }
        }
        console.log(`checkpoint8`)
    
        let vk1_ux = new Array(m[k])
        let vk1_vx = new Array(m[k])
        let vk2_vx = new Array(m[k])
        let vk1_zx = []
        let vk1_ax = []
        let combined_i
        let zx_i
        let ax_i
        
        for(var i=0; i<m[k]; i++){
            vk1_ux[i] = await G1.timesFr(buffG1, ux[i])
            vk1_vx[i] = await G1.timesFr(buffG1, vx[i])
            vk2_vx[i] = await G2.timesFr(buffG2, vx[i])
            combined_i = Fr.add(Fr.add(Fr.mul(tau.alpha_u, ux[i]), Fr.mul(tau.alpha_v, vx[i])), wx[i]);
            if(i>=NZeroWires && i<NZeroWires+mPublic[k]){
                zx_i=Fr.mul(combined_i, Fr.inv(tau.gamma_z));
                vk1_zx.push(await G1.timesFr(buffG1, zx_i))
            }
            else{
                ax_i=Fr.mul(combined_i, Fr.inv(tau.gamma_a));
                vk1_ax.push(await G1.timesFr(buffG1, ax_i))
            }
        }

        //console.log('temp test')
        //console.log('ux: ', ux)
        //console.log('vx: ', vx)
        //console.log('wx: ', wx)
        //console.log('temp test pass')
        // Test code 4//
        // To test [z^(k)_i(x)]_G and [a^(k)_i(x)]_G in sigma_G
        if(TESTFLAG){
            console.log(`Running Test 4`)
            let vk2_alpha_v = await G2.timesFr(buffG2, tau.alpha_v)
            let vk1_wx_i
            let res=0;
            for(var i=0; i<m[k]; i++){ // 모든 i 대신 랜덤한 몇 개의 i만 해봐도 good
                vk1_wx_i = await G1.timesFr(buffG1, wx[i])
                if(i>=NZeroWires && i<NZeroWires+mPublic[k]){
                    res = await curve.pairingEq(vk1_zx[i-NZeroWires],  await G2.neg(vk2_gamma_z), 
                    vk1_ux[i], vk2_alpha_u,
                    vk1_vx[i], vk2_alpha_v,
                    vk1_wx_i, buffG2);
                }
                else{
                    res = await curve.pairingEq(vk1_ax[Math.max(0,i-mPublic[k])],  await G2.neg(vk2_gamma_a),
                    vk1_ux[i], vk2_alpha_u,
                    vk1_vx[i], vk2_alpha_v,
                    vk1_wx_i, buffG2)
/*                     if (k==6 && i==0){
                        console.log('k: ', k)
                        console.log('i: ', i)
                        console.log('i-mPublic: ', i-mPublic[k])
                        console.log('vk1_ax: ', vk1_ax)
                    } */
                    
                }
                if(res == false){
                    console.log('k: ', k)
                    console.log('i: ', i)
                }
                assert(res)
            }   
            console.log(`Test 4 finished`)
        }
        // End of the test code 4//

        // Test code 5//
        // Init: s_D=1, min_s_max=1, r1csName = (any small subcircuit)
        // Hardcode any testing wire instance and witness (in BigInt) into: const wire = new Array(m[0])
        if(TESTFLAG && k==6) // k==6 --> MOD subcircuit, c2 mod c3 = c1 <==> c4*c3+c1 = c2 <==> c4*c3 = -c1+c2
        {
            console.log('Running Test 5')
            const t_x=Fr.mul(Fr.sub(await Fr.exp(x,n),Fr.one), Fr.sub(await Fr.exp(y,s_max),Fr.one));
            const witness = [1, 4, 7, 3, 1];
            // c0=1 (unused), c1=4, c2=7, c3=3, c4=1 <==> 1*3 = -4 + 7
            // one constraint with U[0]=[1], Uid[0]=[4], V[0]=[1], Vid[0]=[3], W[0]=[-1, 1], Wid[0]=[1,2]
            console.log('Uid[0]: ',Uid[0])
            console.log('Vid[0]: ',Vid[0])
            console.log('Wid[0]: ',Wid[0])
            let vk1_U
            let vk2_V
            let vk1_Z
            let vk1_A
            vk1_U = await G1.timesFr(buffG1, Fr.e(0))
            vk2_V = await G2.timesFr(buffG2, Fr.e(0))
            vk1_Z = vk1_U
            vk1_A = vk1_U
            for(var i=0; i<m[k]; i++){
                vk1_U = await G1.add(vk1_U, await G1.timesFr(vk1_ux[i], Fr.e(witness[i])))
                vk2_V = await G2.add(vk2_V, await G2.timesFr(vk2_vx[i], Fr.e(witness[i])))
                if( i>=NZeroWires && i<NZeroWires+mPublic[k] ){
                    vk1_Z = await G1.add(vk1_Z, await G1.timesFr(vk1_zx[i-NZeroWires], Fr.e(witness[i])))
                } else {
                    vk1_A = await G1.add(vk1_A, await G1.timesFr(vk1_ax[Math.max(0,i-mPublic[k])], Fr.e(witness[i])))
                }
            }
            // let LHS1
            // let LHS2
            // let LHS3
            // let RHS
            // LHS1 = pairing( vk1_U, vk2_V )
            // LHS2 = pairing( vk1_U, vk2_alpha_u )
            // LHS3 = pairing( vk1_alpha_v, vk2_V )
            // RHS1 = pairing( vk1_Z, vk2_gamma_r )
            // RHS2 = pairing( vk1_A, vk2_gamma_a )
            // assert( Fr.mul(Fr.mul(LHS1, LHS2), LHS3) == RHS )
            res = await curve.pairingEq(vk1_U, vk2_V,
                vk1_U, vk2_alpha_u,
                vk1_alpha_v, vk2_V,
                vk1_Z,  await G2.neg(vk2_gamma_z),
                vk1_A,  await G2.neg(vk2_gamma_a))
            assert(res)
            console.log(`Test 5 finished`)
        }
        // End of the test code 5//
        await startWriteSection(fdRS, 5+k);
        console.log(`checkpoint9`)
        let multiplier
        let vk1_uxy_ij
        let vk1_vxy_ij
        let vk2_vxy_ij
        let vk1_zxy_ij
        let vk1_axy_ij
        for(var i=0; i < m[k]; i++){
            multiplier=Fr.inv(Fr.e(s_max))
            vk1_uxy_ij= await G1.timesFr(vk1_ux[i], multiplier)
            await zkeyUtils.writeG1(fdRS, curve, vk1_uxy_ij)
            for(var j=1; j < s_max; j++){
                multiplier=Fr.mul(multiplier, y)
                vk1_uxy_ij= await G1.timesFr(vk1_ux[i], multiplier)
                await zkeyUtils.writeG1(fdRS, curve, vk1_uxy_ij)
            }
        }
        for(var i=0; i < m[k]; i++){
            multiplier=Fr.inv(Fr.e(s_max))
            vk1_vxy_ij= await G1.timesFr(vk1_vx[i], multiplier)
            await zkeyUtils.writeG1(fdRS, curve, vk1_vxy_ij)
            for(var j=1; j < s_max; j++){
                multiplier=Fr.mul(multiplier, y)
                vk1_vxy_ij= await G1.timesFr(vk1_vx[i], multiplier)
                await zkeyUtils.writeG1(fdRS, curve, vk1_vxy_ij)
            }
        }
        for(var i=0; i < m[k]; i++){
            multiplier=Fr.inv(Fr.e(s_max))
            vk2_vxy_ij= await G2.timesFr(vk2_vx[i], multiplier)
            await zkeyUtils.writeG2(fdRS, curve, vk2_vxy_ij)
            for(var j=1; j < s_max; j++){
                multiplier=Fr.mul(multiplier, y)
                vk2_vxy_ij= await G2.timesFr(vk2_vx[i], multiplier)
                await zkeyUtils.writeG2(fdRS, curve, vk2_vxy_ij)
            }
        }
        console.log(`checkpoint10`)
        for(var i=0; i < mPublic[k]; i++){
            multiplier=Fr.inv(Fr.e(s_max))
            vk1_zxy_ij= await G1.timesFr(vk1_zx[i], multiplier)
            await zkeyUtils.writeG1(fdRS, curve, vk1_zxy_ij)
            for(var j=1; j < s_max; j++){
                multiplier=Fr.mul(multiplier, y)
                vk1_zxy_ij= await G1.timesFr(vk1_zx[i], multiplier)
                await zkeyUtils.writeG1(fdRS, curve, vk1_zxy_ij)
            }
        }
        for(var i=0; i < mPrivate[k]; i++){
            multiplier=Fr.inv(Fr.e(s_max))
            vk1_axy_ij= await G1.timesFr(vk1_ax[i], multiplier)
            await zkeyUtils.writeG1(fdRS, curve, vk1_axy_ij)
            for(var j=1; j < s_max; j++){
                multiplier=Fr.mul(multiplier, y)
                vk1_axy_ij= await G1.timesFr(vk1_ax[i], multiplier)
                await zkeyUtils.writeG1(fdRS, curve, vk1_axy_ij)
            }
        }
        await endWriteSection(fdRS)
        console.log(`checkpoint11`)
    }
    

    await fdRS.close()
    console.log(`checkpoint12`)

    // End of the theta_G section
    ///////////
    


    function createTauKey(Field, rng) {
        if (rng.length != 6){
            console.log(`checkpoint3`)
            throw new Error('It should have six elements.')
        } 
        const key = {
            x: Field.fromRng(rng[0]),
            y: Field.fromRng(rng[1]),
            alpha_u: Field.fromRng(rng[2]),
            alpha_v: Field.fromRng(rng[3]),
            gamma_a: Field.fromRng(rng[4]),
            gamma_z: Field.fromRng(rng[5])
        }
        return key
    }

    async function processConstraints() { 
        let r1csPos = 0;
        let results={};
        const n_k = r1cs[k].nConstraints;
        let U = new Array(n_k);
        let Uid = new Array(n_k);
        let V = new Array(n_k);
        let Vid = new Array(n_k);
        let W = new Array(n_k);
        let Wid = new Array(n_k);
    
        function r1cs_readULE32toUInt() {
            const buff = sR1cs[k].slice(r1csPos, r1csPos+4);
            r1csPos += 4;
            const buffV = new DataView(buff.buffer);
            return buffV.getUint32(0, true)
        }
        function r1cs_readULE256toFr() {
            const buff = sR1cs[k].slice(r1csPos, r1csPos+32);
            r1csPos += 32;
            const buffV = curve.Fr.fromRprLE(buff);
            return buffV
        }
        for (var c=0; c<n_k; c++) {
            //if ((logger)&&(c%10000 == 0)) logger.debug(`processing constraints: ${c}/${r1cs.nConstraints}`);
            const nA = r1cs_readULE32toUInt();
            let coefsA = new Array(nA);
            let idsA = new Array(nA);
            for (let i=0; i<nA; i++) {
                idsA[i] = r1cs_readULE32toUInt();
                coefsA[i] = r1cs_readULE256toFr();
            }
            //if (typeof A[s] === "undefined") A[s] = [];
            U[c] = coefsA;
            Uid[c] = idsA;

            const nB = r1cs_readULE32toUInt();
            let coefsB = new Array(nB);
            let idsB = new Array(nB);
            for (let i=0; i<nB; i++) {
                idsB[i] = r1cs_readULE32toUInt();
                coefsB[i] = r1cs_readULE256toFr();
            }
            V[c] = coefsB;
            Vid[c] = idsB;
    
            const nC = r1cs_readULE32toUInt();
            let coefsC = new Array(nC);
            let idsC = new Array(nC);
            for (let i=0; i<nC; i++) {
                idsC[i] = r1cs_readULE32toUInt();
                coefsC[i] = r1cs_readULE256toFr();
            }
            W[c] = coefsC;
            Wid[c] = idsC;
        }
        results.U = U;
        results.Uid = Uid;
        results.V = V;
        results.Vid = Vid;
        results.W = W;
        results.Wid = Wid;
        return results
    }
}
