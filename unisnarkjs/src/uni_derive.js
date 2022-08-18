import * as curves from "./curves.js"
import * as misc from './misc.js'
import * as zkeyUtils from "./uni_zkey_utils.js";
import * as binFileUtils from "@iden3/binfileutils";
import * as wtnsUtils from "./wtns_utils.js";
import {
    readBinFile,
    createBinFile,
    readSection,
    writeBigInt,
    startWriteSection,
    endWriteSection,
} from "@iden3/binfileutils";
import * as fastFile from "fastfile";
import { assert } from "chai";

export function createTauKey(Field, rng) {
    if (rng.length != 6) throw new Error('It should have six elements.')
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

export default async function uniDerive(RSName, cRSName, IndSetVName, IndSetPName, OpListName) {
    const {fd: fdRS, sections: sectionsRS} = await binFileUtils.readBinFile('resource/'+RSName+'.urs', "zkey", 2, 1<<25, 1<<23);
    const urs = {}
    urs.param = await zkeyUtils.readRSParams(fdRS, sectionsRS)
    urs.content = await zkeyUtils.readRS(fdRS, sectionsRS, urs.param)

    const fdIdV = await fastFile.readExisting('resource/'+IndSetVName +'.bin', 1<<25, 1<<23);
    const fdIdP = await fastFile.readExisting('resource/'+IndSetPName +'.bin', 1<<25, 1<<23);
    const fdOpL = await fastFile.readExisting('resource/'+OpListName +'.bin', 1<<25, 1<<23);

    const IdSetV = await zkeyUtils.readIndSet(fdIdV)
    const IdSetP = await zkeyUtils.readIndSet(fdIdP)
    const OpList = await zkeyUtils.readOpList(fdOpL)
    // IdSet#.set, IdSet#.PreImgs
    
    await fdIdV.close()
    await fdIdP.close()
    await fdOpL.close()

    const ParamR1cs = urs.param.r1cs
    const curve = urs.param.curve
    const G1 = urs.param.curve.G1
    const G2 = urs.param.curve.G2
    const Fr = urs.param.curve.Fr
    const buffG1 = curve.G1.oneAffine;
    const buffG2 = curve.G2.oneAffine;
    const s_max = urs.param.s_max
    const s_D = urs.param.s_D
    const omega_y = await Fr.e(urs.param.omega_y)

    console.log('smax: ', s_max)
    console.log('checkpoint0')

    const mPublic = IdSetV.set.length // length of input instance + the total number of subcircuit outputs
    const mPrivate = IdSetP.set.length 
    const m = mPublic + mPrivate
    const NZeroWires = 1

    let PreImgSet
    let PreImgSize
    let mPublic_k
    let vk1_term
    let vk2_term
    let arrayIdx
    let kPrime
    let s_kPrime
    let iPrime
    let OmegaFactor

    let vk1_zxy = new Array(mPublic)
    for(var i=0; i<mPublic; i++){
        PreImgSet = IdSetV.PreImgs[i]
        PreImgSize = IdSetV.PreImgs[i].length
        vk1_zxy[i] = await G1.timesFr(buffG1, Fr.e(0))
        for(var j=0; j<s_max; j++){
            for(var PreImgIdx=0; PreImgIdx<PreImgSize; PreImgIdx++){
                kPrime = PreImgSet[PreImgIdx][0]
                s_kPrime = OpList[kPrime]
                iPrime = PreImgSet[PreImgIdx][1]
                mPublic_k = ParamR1cs[s_kPrime].mPublic
                
                if(!(iPrime >= NZeroWires && iPrime < NZeroWires+mPublic_k)){
                    throw new Error('invalid access to vk1_zxy_kij')
                }
                arrayIdx = iPrime-NZeroWires
                vk1_term = urs.content.theta_G.vk1_zxy_kij[s_kPrime][arrayIdx][j]
                OmegaFactor = Fr.inv(await Fr.exp(omega_y, kPrime*j))
                vk1_term = await G1.timesFr(vk1_term, OmegaFactor)
                vk1_zxy[i] = await G1.add(vk1_zxy[i], vk1_term)
            }
        }
    }

    console.log('checkpoint1')

    let vk1_axy = new Array(mPrivate)
    for(var i=0; i<mPrivate; i++){
        PreImgSet = IdSetP.PreImgs[i]
        PreImgSize = IdSetP.PreImgs[i].length
        vk1_axy[i] = await G1.timesFr(buffG1, Fr.e(0))
        for(var j=0; j<s_max; j++){
            for(var PreImgIdx=0; PreImgIdx<PreImgSize; PreImgIdx++){
                kPrime = PreImgSet[PreImgIdx][0]
                s_kPrime = OpList[kPrime]
                iPrime = PreImgSet[PreImgIdx][1]
                mPublic_k = ParamR1cs[s_kPrime].mPublic
 
                if(iPrime < NZeroWires){
                    arrayIdx = iPrime
                } else if(iPrime >= NZeroWires+mPublic_k){
                    arrayIdx = iPrime-mPublic_k
                } else{
                    throw new Error('invalid access to vk1_axy_kij')
                }

                vk1_term = urs.content.theta_G.vk1_axy_kij[s_kPrime][arrayIdx][j]
                OmegaFactor = Fr.inv(await Fr.exp(omega_y, kPrime*j))
                vk1_term = await G1.timesFr(vk1_term, OmegaFactor)
                vk1_axy[i] = await G1.add(vk1_axy[i], vk1_term)
            }
        }
    }

    console.log('checkpoint2')

    let vk1_uxy = new Array(m)
    for(var i=0; i<m; i++){
        if(IdSetV.set.indexOf(i) > -1){
            arrayIdx = IdSetV.set.indexOf(i)
            PreImgSet = IdSetV.PreImgs[arrayIdx]
        } else {
            arrayIdx = IdSetP.set.indexOf(i)
            PreImgSet = IdSetP.PreImgs[arrayIdx]
        }
        PreImgSize = PreImgSet.length
        vk1_uxy[i] = await G1.timesFr(buffG1, Fr.e(0))
        for(var j=0; j<s_max; j++){
            for(var PreImgIdx=0; PreImgIdx<PreImgSize; PreImgIdx++){
                kPrime = PreImgSet[PreImgIdx][0]
                s_kPrime = OpList[kPrime]
                iPrime = PreImgSet[PreImgIdx][1]
                vk1_term = urs.content.theta_G.vk1_uxy_kij[s_kPrime][iPrime][j]
                OmegaFactor = Fr.inv(await Fr.exp(omega_y, kPrime*j))
                vk1_term = await G1.timesFr(vk1_term, OmegaFactor)
                vk1_uxy[i] = await G1.add(vk1_uxy[i], vk1_term)
            }
        }
    }

    console.log('checkpoint3')

    let vk1_vxy = new Array(m)
    for(var i=0; i<m; i++){
        if(IdSetV.set.indexOf(i) > -1){
            arrayIdx = IdSetV.set.indexOf(i)
            PreImgSet = IdSetV.PreImgs[arrayIdx]
        } else {
            arrayIdx = IdSetP.set.indexOf(i)
            PreImgSet = IdSetP.PreImgs[arrayIdx]
        }
        PreImgSize = PreImgSet.length
        vk1_vxy[i] = await G1.timesFr(buffG1, Fr.e(0))
        for(var j=0; j<s_max; j++){
            for(var PreImgIdx=0; PreImgIdx<PreImgSize; PreImgIdx++){
                kPrime = PreImgSet[PreImgIdx][0]
                s_kPrime = OpList[kPrime]
                iPrime = PreImgSet[PreImgIdx][1]

                vk1_term = urs.content.theta_G.vk1_vxy_kij[s_kPrime][iPrime][j]
                OmegaFactor = Fr.inv(await Fr.exp(omega_y, kPrime*j))
                vk1_term = await G1.timesFr(vk1_term, OmegaFactor)
                vk1_vxy[i] = await G1.add(vk1_vxy[i], vk1_term)
            }
        }
    }

    console.log('checkpoint4')

    let vk2_vxy = new Array(m)
    for(var i=0; i<m; i++){
        if(IdSetV.set.indexOf(i) > -1){
            arrayIdx = IdSetV.set.indexOf(i)
            PreImgSet = IdSetV.PreImgs[arrayIdx]
        } else {
            arrayIdx = IdSetP.set.indexOf(i)
            PreImgSet = IdSetP.PreImgs[arrayIdx]
        }
        PreImgSize = PreImgSet.length
        vk2_vxy[i] = await G2.timesFr(buffG2, Fr.e(0))
        for(var j=0; j<s_max; j++){
            for(var PreImgIdx=0; PreImgIdx<PreImgSize; PreImgIdx++){
                kPrime = PreImgSet[PreImgIdx][0]
                s_kPrime = OpList[kPrime]
                iPrime = PreImgSet[PreImgIdx][1]

                vk2_term = urs.content.theta_G.vk2_vxy_kij[s_kPrime][iPrime][j]
                OmegaFactor = Fr.inv(await Fr.exp(omega_y, kPrime*j))
                vk2_term = await G2.timesFr(vk2_term, OmegaFactor)
                vk2_vxy[i] = await G2.add(vk2_vxy[i], vk2_term)
            }
        }
    }

    console.log('checkpoint5')

    const fdcRS = await createBinFile('resource/'+cRSName+".crs", "zkey", 6, 2, 1<<22, 1<<24)
    await binFileUtils.copySection(fdRS, sectionsRS, fdcRS, 1)
    await binFileUtils.copySection(fdRS, sectionsRS, fdcRS, 2)
    await binFileUtils.copySection(fdRS, sectionsRS, fdcRS, 3)
    await binFileUtils.copySection(fdRS, sectionsRS, fdcRS, 4)

    await fdRS.close()
    
    await startWriteSection(fdcRS, 5)
    for(var i=0; i<m; i++){
        await zkeyUtils.writeG1(fdcRS, curve, vk1_uxy[i])
    }
    for(var i=0; i<m; i++){
        await zkeyUtils.writeG1(fdcRS, curve, vk1_vxy[i])
    }
    for(var i=0; i<mPublic; i++){
        await zkeyUtils.writeG1(fdcRS, curve, vk1_zxy[i])
    }
    // vk1_zxy[i] represents the IdSetV.set(i)-th wire of circuit
    for(var i=0; i<mPrivate; i++){
        await zkeyUtils.writeG1(fdcRS, curve, vk1_axy[i])
    }
    // vk1_axy[i] represents the IdSetP.set(i)-th wire of circuit
    await endWriteSection(fdcRS)
    
    
    await startWriteSection(fdcRS, 6)
    for(var i=0; i<m; i++){
        await zkeyUtils.writeG2(fdcRS, curve, vk2_vxy[i])
    }
    await endWriteSection(fdcRS)
    fdcRS.close()
}
