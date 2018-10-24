#!/usr/bin/env python3

"""
Test whether anchors include blocks or not.

./src/bitcoind -regtest -daemon
./src/bitcoin-cli -regtest generate 200
./src/bitcoin-cli -regtest getbalance
./src/bitcoin-cli -regtest sendtoaddress  0.5
./src/bitcoin-cli -regtest sendtoaddress 2N8tfBurwCR9WxtpVfWRvtfLPP8Ruffg98C 0.5
./src/bitcoin-cli -regtest getbalance
./src/bitcoin-cli -regtest sendtoaddress 2N8tfBurwCR9WxtpVfWRvtfLPP8Ruffg98C 50
./src/bitcoin-cli -regtest getbalance
./src/bitcoin-cli -regtest sendtoaddress 2N8tfBurwCR9WxtpVfWRvtfLPP8Ruffg98C 500
./src/bitcoin-cli -regtest getbalance
./src/bitcoin-cli -regtest generate 1
./src/bitcoin-cli -regtest getblock {hash}
"""

from pprint import pprint

from test_framework.test_framework import BitcoinTestFramework


class TestTransactions(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = False

    def run_test(self):
        [node.generate(101) for node in self.nodes]

        print("Generated 101 blocks at each bitcoin node")

        fst = self.nodes[0]
        snd = self.nodes[1]

        fbal = fst.getbalance()
        print("Balance of 1st: ", fbal)

        sbal = snd.getbalance()
        print("Balance of 2nd: ", sbal)

        # -------------------------------------

        saddr = snd.getnewaddress()

        print("Address of 2nd: ", saddr)

        # -------------------------------------

        fst.sendtoaddress(saddr, 1)

        fbal = fst.getbalance()
        print("Balance of 1st: ", fbal)

        sbal = snd.getbalance()
        print("Balance of 2nd: ", sbal)

        # -------------------------------------

        fst.sendtoaddress(saddr, 1)

        fbal = fst.getbalance()
        print("Balance of 1st: ", fbal)

        sbal = snd.getbalance()
        print("Balance of 2nd: ", sbal)

        # -------------------------------------

        hashes = fst.generate(1)
        print("Newly minted block by 1st: ", hashes[0])

        block = fst.getblock(hashes[0])
        pprint(block)

        # -------------------------------------

        fbal = fst.getbalance()
        print("Balance of 1st: ", fbal)

        sbal = snd.getbalance()
        print("Balance of 2nd: ", sbal)


if __name__ == '__main__':
    TestTransactions().main()
