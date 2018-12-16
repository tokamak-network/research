---
id: 1
author: Carl Park
title: Validate State Transition
status: Draft
created: 2018-11-26
---

TrueBit verification game provides the way of validating state transition function using solevm on ethereum. So when a malicious block is committed to the root chain, the computational result should be verified, meanning that the EVM is correctly executed. When we consider validity of state transition function by block, the game is played as follow.

1.  Block committer(operator for ORB / NRB, anyone for URB) uploads a block with some Ether as deposit.

2.  Challenger watch the upload and validate it within his own machine. If he found that result from 1 is not same as his, he initiate verification game with some Ether as deposit.

3.  If there are open game session, wait until they are closed.

4.  Then, a session for the challenger is open, challenger query the output with specific **transaction index** and committer respond it with the hash of EVM state just after the transaction is executed.

5.  challenger can quickly find the transaction that is executed in a wrong way by bisecting the search range.

6.  After challenger found the transaction, then he query the output with **EVM runtime index** (like program counter, but index only increases) of the transition.

7.  Committer respond it in the same way as transaction.

8.  When the index_pre + 1 == index_post (at the end of binary search), verifier contract (based on solevm) execute evm and determine the winner.

9.  If loser is committer, block is reverted and commiter's deposit is sent to challenger as reward.

10. Otherwise, challenger's deposit is burn. We can give a reward to operator (not user who commit URB) according to economic paper.

Above process can verify the state transition function of _block_.
