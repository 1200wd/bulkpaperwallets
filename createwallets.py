#
# Bulk Paper Wallets
# (c) March 2017 1200 Development Amsterdam
#
# Generate Bitcoin Paper Wallets in Bulk and fund them. Wallets will be saved as PDF files.
#
# Published under GNU GENERAL PUBLIC LICENSE see LICENSE file for more details.
# WARNING: This software is still under development, only use if you understand the code and known what you are doing.
# So use at your own risk!
#

import sys
import os
import argparse
from builtins import input
import binascii
import qrcode
import pdfkit
from jinja2 import Template
from bitcoinlib.wallets import HDWallet, wallet_exists, delete_wallet, list_wallets
from bitcoinlib.keys import Key, HDKey
from bitcoinlib.transactions import Transaction, Input, Output
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.services.services import Service


# Bitcoins uitdelen definitions
DEFAULT_NETWORK = 'bitcoin'
DEFAULT_WALLET_NAME = "Bulk Paper Wallet"
# OUTPUT_NUMBER = 5
# OUTPUT_FEE = 10000
# OUTPUT_AMOUNT = int((135914715 / 5) - OUTPUT_FEE)
# PK_SENTENCE = 'dizzy shoe popular funny purse street drink jazz call key local movie'

INSTALL_DIR = os.path.dirname(__file__)
WALLET_DIR = os.path.join(INSTALL_DIR, 'wallets')
if not os.path.exists(WALLET_DIR):
    os.makedirs(WALLET_DIR)

# Unspent transaction output to use as input
# TODO: Allow more then 1 input
# input_utxo = 'adee8bdd011f60e52949b65b069ff9f19fc220815fdc1a6034613ed1f6b775f1'
# input_index = 0
# input_pk = 'cRMjy1LLMPsVU4uaAt3br8Ft5vdJLx6prY4Sx7WjPARrpYAnVEkV'


class BulkPaperWallet(HDWallet):

    def create_bulk_transaction(self, wallet):
        # Create Transaction and add input and outputs
        t = Transaction(network=self.network)
        ki = Key(input_pk)
        t.add_input(input_utxo, input_index, public_key=ki.public())

        output_keys = []
        for _ in range(0, OUTPUT_NUMBER):
            nk = wallet.new_key()
            t.add_output(OUTPUT_AMOUNT, address=nk.address)
            output_keys.append(nk)

        t.sign(ki.private_byte(), 0)
        if not t.verify():
            raise Exception("Could not verify this transaction: %s" % t.get())

        return

    def create_paper_wallets(self, output_keys):
        # Create Paper wallets
        for wallet_key in output_keys:
            address_img = qrcode.make(wallet_key.address)
            filename_pre = "%s/%d-" % (WALLET_DIR, wallet_key.key_id)
            address_img.save(filename_pre+'address.png', 'PNG')

            priv_img = qrcode.make(wallet_key.k.private().wif())
            priv_img.save(filename_pre+'privatekey.png', 'PNG')

            f = open('wallet_template.html', 'r')
            template = Template(f.read())
            wallet_name = "%s %d" % (self.wallet_name, wallet_key.key_id)
            wallet_str = template.render(
                install_dir=INSTALL_DIR,
                filename_pre=filename_pre,
                wallet_name=wallet_name,
                private_key=wallet_key.k.private().wif(),
                address=wallet_key.address)
            pdfkit.from_string(wallet_str, filename_pre+'wallet.pdf')


def parse_args():
    parser = argparse.ArgumentParser(description='Create Bulk Paper Wallets')
    parser.add_argument('--wallet-name', '-w', default=DEFAULT_WALLET_NAME,
                        help="Name of wallet to create or open. Used to store your all your wallet keys "
                             "and will be printed on each paper wallet")
    parser.add_argument('--network', '-n', help="Specify 'bitcoin', 'testnet' or other supported network",
                        default=DEFAULT_NETWORK)
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('--outputs', '-o', nargs="*", type=float,
                        help="List of output values. For example '-o 1 2 3' creates 3 wallets with a value of "
                             "1, 2 and 3 bitcoin successively")
    group1.add_argument('--outputs-import', '-f',
                        help="Filename of comma seperated value list of output values and optional wallet names. "
                             "Example: 1.51, John")
    parser.add_argument('--outputs-repeat', '-r', type=int,
                        help="Repeat the outputs OUTPUTS_REPEAT times. For example 'createwallet.py -o 5 -r 10' "
                             "will create 10 wallets with 5 bitcoin")
    parser.add_argument('--input-key', '-i',
                        help="Private key to create transaction input. If not specified a private key "
                             "and address to send bitcoins to will be created")
    parser.add_argument('--wallet-remove',
                        help="Name of wallet to remove, all keys and related information will be deleted")
    parser.add_argument('--list-wallets', '-l', action='store_true',
                        help="List all known wallets in bitcoinlib database")
    parser.add_argument('--recover-wallet-passphrase',
                        help="Passphrase of 12 words to recover and regenerate a previous wallet")

    pa = parser.parse_args()
    if pa.outputs_repeat and pa.outputs is None:
        parser = argparse.ArgumentParser()
        parser.error("--output_repeat requires --outputs")
    return pa

if __name__ == '__main__':
    args = parse_args()

    wallet_name = args.wallet_name
    network = args.network

    if args.list_wallets:
        print("\nBitcoinlib wallets:")
        for w in list_wallets():
            print(w['name'])

    if args.wallet_remove:
        if not wallet_exists(args.wallet_remove):
            print("Wallet '%s' not found" % args.wallet_remove)
            sys.exit()
        inp = input("\nWallet '%s' with all keys and will be removed, without private key it cannot be restored."
                    "\nPlease retype exact name of wallet to proceed: " % args.wallet_remove)
        if inp == args.wallet_remove:
            print(delete_wallet(args.wallet_remove))
            sys.exit()

    if wallet_exists(wallet_name):
        wallet = BulkPaperWallet(wallet_name)
        print("\nOpen wallet '%s' (%s network)" % (wallet_name, network))
    else:
        print("\nCREATE wallet '%s' (%s network)" % (wallet_name, network))
        if not args.recover_wallet_passphrase:
            words = Mnemonic('english').generate()
            print("\nYour mnemonic private key sentence is: %s" % words)
            print("\nPlease write down on paper and backup. IF YOU LOSE THIS PRIVATE KEY ALL COINS ARE LOST!")
            inp = input("\nType 'yes' if you understood and wrote down your key: ")
            if inp not in ['yes', 'Yes', 'YES']:
                print("Exiting...")
                sys.exit()
        else:
            words = args.recover_wallet_passphrase

        seed = binascii.hexlify(Mnemonic().to_seed(words))
        hdkey = HDKey().from_seed(seed, network=network)
        wallet = BulkPaperWallet.create(name=wallet_name, network=network, key=hdkey.extended_wif())
        wallet.new_account()

    if args.outputs_import:
        pass
        # TODO: import amount and wallet names from csv
    else:
        outputs = [{'amount': o} for o in args.outputs]

    t = Transaction(network=network)
    output_keys = []
    total_amount = 0
    for o in outputs:
        nk = wallet.new_key()
        t.add_output(o['amount'], nk.address)
        output_keys.append(nk)
        total_amount += o['amount']

    estimated_fee = (200 + len(t.raw())) * 200
    print("Estimated fee is for this transaction is %d" % estimated_fee)
    if not args.input_key:
        # TODO: create new key and ask for funds
        pass

    # TODO write code to look for UTXO's

