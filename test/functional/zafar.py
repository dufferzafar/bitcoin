#!/usr/bin/env python3

"""Boilerplate copied from mining_basic.py."""

from pprint import pprint

from binascii import b2a_hex

from test_framework.blocktools import create_coinbase
from test_framework.mininode import CBlock
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal
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
    block.nNonce = 0

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
        # TODO: Test why it doesn't work with a single node
        self.num_nodes = 2
        self.setup_clean_chain = False

    def run_test(self):
        node = self.nodes[0]

        node.generate(1)
        tmpl = node.getblocktemplate()

        # Add a block
        # block = new_block(tmpl, 1)
        # rsp = node.submitblock(b2x(block.serialize()))

        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, before: ", cw)

        block = new_block(tmpl, 1)
        node.submitanchor(b2x(block.serialize()))

        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, after : ", cw)

        # Ask the other node, what the state is
        node = self.nodes[1]
        tmpl = node.getblocktemplate()

        cw = node.getblockheader(tmpl["previousblockhash"])["chainwork"]
        print("Chainwork, node 1: ", cw)

        # rsp = node.submitanchor(b2x(block.serialize()))
        # block = new_block(tmpl, 3)
        # rsp = node.submitanchor(b2x(block.serialize()))
        # block = new_block(tmpl, 4)
        # rsp = node.submitanchor(b2x(block.serialize()))

        # print(rsp)


if __name__ == '__main__':
    # SubmitBlocks().main()
    SubmitAnchors().main()
