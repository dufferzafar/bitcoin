#!/usr/bin/env python3

"""Boilerplate copied from mining_basic.py."""

import random
import time

from pprint import pprint

from binascii import b2a_hex

from test_framework.blocktools import create_coinbase
from test_framework.mininode import CBlock
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, disconnect_nodes
# from test_framework.util import assert_raises_rpc_error


def b2x(b):
    return b2a_hex(b).decode('ascii')


def assert_template(node, block, expect, rehash=True):
    if rehash:
        block.hashMerkleRoot = block.calc_merkle_root()
    rsp = node.getblocktemplate(
        {'data': b2x(block.serialize()), 'mode': 'proposal'})
    assert_equal(rsp, expect)


def new_block(tmpl, ht=1):
    # Create a coinbase transaction
    coinbase_tx = create_coinbase(height=int(tmpl["height"]) + 1)
    coinbase_tx.vin[0].nSequence = 2 ** 32 - ht
    coinbase_tx.rehash()

    # Create a block
    # TODO: Add helper function to create a block from a template?
    block = CBlock()

    block.nVersion = tmpl["version"]
    block.hashPrevBlock = int(tmpl["previousblockhash"], 16)
    block.nTime = tmpl["curtime"]
    block.nBits = int(tmpl["bits"], 16)
    block.nNonce = random.randint(1, 100)

    # Add coinbase to the block
    # TODO: More transactions can be added here
    block.vtx = [coinbase_tx]
    block.hashMerkleRoot = block.calc_merkle_root()

    # Proof of work happens here
    block.solve()

    return block


class SubmitBlocks(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = False

    def run_test(self):
        node = self.nodes[0]

        # MI = node.getmininginfo()
        # print(MI)

        print()
        print("==> Generating Blocks")
        print()

        # NOTE: Look into why nodes start with an initial block count of 200?
        rsp = node.getblockcount()
        self.log.info("count: at start: %d" % rsp)

        # NOTE: Mine a block to leave initial block download ?
        node.generate(1)
        rsp = node.getblockcount()
        self.log.info("count: after mining one: %d" % rsp)

        tmpl = node.getblocktemplate()

        block = new_block(tmpl, 1)
        rsp = node.submitblock(b2x(block.serialize()))
        rsp = node.getblockcount()
        # print(block.hash)

        self.log.info("count: after proposing first from outside: %d" % rsp)

        # block = new_block(tmpl, 2)
        # print(block.hash)

        # rsp = node.submitblock(b2x(block.serialize()))
        # rsp = node.getblockcount()
        # self.log.info("count: after proposing second from outside: %d" % rsp)

        rsp = node.getblockheader(block.hash)
        pprint(rsp)

        print()

        # assert(False)


class SubmitAnchors(BitcoinTestFramework):

    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = False

    def run_test(self):
        node = self.nodes[0]
        node.generate(5)
        tmpl = node.getblocktemplate()

        # Add a block
        # block = new_block(tmpl, 1)
        # node.submitblock(b2x(block.serialize()))

        # print(node.generateanchor())

        print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, before: ", cw)

        block = new_block(tmpl, 1)
        node.submitanchor(b2x(block.serialize()))

        print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, after : ", cw)

        # Ask the other node, what the state is
        node = self.nodes[1]

        print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, node 1: ", cw)

        block = new_block(tmpl, 1)
        node.submitanchor(b2x(block.serialize()))

        time.sleep(random.randint(1, 5))

        # block = new_block(tmpl, 4)
        # rsp = node.submitanchor(b2x(block.serialize()))

        print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, node 1: ", cw)

        # raise False


class GenerateAnchors(BitcoinTestFramework):

    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = False

    def run_test(self):
        node = self.nodes[0]
        node.generate(5)
        tmpl = node.getblocktemplate()

        # print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, before: ", cw)

        node.generateanchor()
        time.sleep(3)

        # print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, after : ", cw)

        # Ask the other node, what the state is
        node = self.nodes[1]

        # print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, node 1: ", cw)

        node.generateanchor()

        # time.sleep(random.randint(1, 5))

        # print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, node 1: ", cw)

        raise False


class CreateForksPy(BitcoinTestFramework):

    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = False

    def run_test(self):
        node = self.nodes[0]
        node.generate(1)

        tmpl = node.getblocktemplate()

        # print(tmpl)

        # print("Previous Block Hash: ", tmpl["previousblockhash"])
        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, before: ", tmpl["previousblockhash"], cw, int(cw, 16))

        block = new_block(tmpl, 1)
        node.submitblock(b2x(block.serialize()))

        cw = node.getblockheader(block.hash)["chainwork"]
        print("Chainwork, block 1: ", block.hash, cw, int(cw, 16))

        block = new_block(tmpl, 1)
        node.submitblock(b2x(block.serialize()))

        cw = node.getblockheader(block.hash)["chainwork"]
        print("Chainwork, block 2: ", block.hash, cw, int(cw, 16))

        print(node.getchaintips())


class CreateForksCpp(BitcoinTestFramework):

    def set_test_params(self):
        self.num_nodes = 2
        self.setup_clean_chain = False

    def run_test(self):
        node1 = self.nodes[0]
        node2 = self.nodes[1]

        b0 = node1.generate(1)[0]
        b0 = node1.getblockheader(b0)
        cw0 = b0["chainwork"]
        b0 = b0["hash"]
        print("parent: ", b0, cw0, int(cw0, 16))

        # Both nodes now have same state

        # Disconnect both nodes
        disconnect_nodes(self.nodes[0], 1)
        disconnect_nodes(self.nodes[1], 0)

        b1 = node1.generate(1)[0]
        b1 = node1.getblockheader(b1)
        p1 = b1["previousblockhash"]
        cw1 = b1["chainwork"]
        b1 = b1["hash"]

        b2 = node2.generate(1)[0]
        b2 = node2.getblockheader(b2)
        p2 = b2["previousblockhash"]
        cw2 = b2["chainwork"]
        b2 = b2["hash"]

        # Both these blocks should have same chainwork
        print("block 1: ", p1, b1, int(cw1, 16))
        print("block 2: ", p2, b2, int(cw2, 16))


class GenerateAnchorHashes(BitcoinTestFramework):

    def set_test_params(self):
        self.num_nodes = 3
        self.setup_clean_chain = False

    def run_test(self):
        node = self.nodes[0]

        # A small-ish block chain
        node.generate(1)

        # Successively generate lots of blocks
        hs = set()

        for _ in range(100):
            node = random.choice(self.nodes)
            h = node.generateanchor()[0]

            if h in hs:
                print("Collision!")

            hs.add(h)
            print(h)
            time.sleep(0.5)



if __name__ == '__main__':
    # SubmitBlocks().main()
    # SubmitAnchors().main()
    # GenerateAnchors().main()
    # CreateForksPy().main()
    # CreateForksCpp().main()
    GenerateAnchorHashes().main()
