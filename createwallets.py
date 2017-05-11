# -*- coding: iso-8859-15 -*-
#
# Bulk Paper Wallets
# Generate Bitcoin Paper Wallets in Bulk and fund them. Wallets will be saved as PDF files.
# © 2017 April - 1200 Web Development <http://1200wd.com/>
#
# Published under GNU GENERAL PUBLIC LICENSE see LICENSE file for more details.
# WARNING: This software is still under development, only use if you understand the code and known what you are doing.
# So use at your own risk!
#

import sys
import os
import argparse
import binascii
import qrcode
import pdfkit
from jinja2 import Template
from bitcoinlib.wallets import HDWallet, wallet_exists, delete_wallet, list_wallets
from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.networks import Network
from bitcoinlib.services.services import Service


try:
    input = raw_input
except NameError:
    pass


DEFAULT_NETWORK = 'bitcoin'
DEFAULT_WALLET_NAME = "Bulk Paper Wallet"
INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))
WALLET_DIR = os.path.join(INSTALL_DIR, 'wallets')
if not os.path.exists(WALLET_DIR):
    os.makedirs(WALLET_DIR)


class BulkPaperWallet(HDWallet):

    # def create_bulk_transaction(self, wallet):
    #     # Create Transaction and add input and outputs
    #     t = Transaction(network=self.network)
    #     ki = Key(input_pk)
    #     t.add_input(input_utxo, input_index, public_key=ki.public())
    #
    #     output_keys = []
    #     for _ in range(0, OUTPUT_NUMBER):
    #         nk = wallet.new_key()
    #         t.add_output(OUTPUT_AMOUNT, address=nk.address)
    #         output_keys.append(nk)
    #
    #     t.sign(ki.private_byte(), 0)
    #     if not t.verify():
    #         raise Exception("Could not verify this transaction: %s" % t.get())
    #
    #     return

    def create_paper_wallets(self, output_keys):
        count = 0
        for wallet_key in output_keys:
            address_img = qrcode.make(wallet_key.address)
            filename_pre = "%s/%d-" % (WALLET_DIR, wallet_key.key_id)
            address_img.save(filename_pre+'address.png', 'PNG')

            priv_img = qrcode.make(wallet_key.key_wif)
            priv_img.save(filename_pre+'privatekey.png', 'PNG')

            f = open('wallet_template.html', 'r')
            template = Template(f.read())
            wallet_name = "%s %d" % (self.name, wallet_key.key_id)
            wallet_str = template.render(
                install_dir=INSTALL_DIR,
                filename_pre=filename_pre,
                wallet_name=wallet_name,
                private_key=wallet_key.key_wif,
                address=wallet_key.address)
            print("Generate wallet %d" % wallet_key.key_id)
            pdfkit.from_string(wallet_str, filename_pre+'wallet.pdf')
            count += 1
        print("A total of %d paper wallets have been created" % count)


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
    # parser.add_argument('--input-key', '-i',
    #                     help="Private key to create transaction input. If not specified a private key "
    #                          "and address to send bitcoins to will be created")
    parser.add_argument('--wallet-remove',
                        help="Name of wallet to remove, all keys and related information will be deleted")
    parser.add_argument('--list-wallets', '-l', action='store_true',
                        help="List all known wallets in bitcoinlib database")
    parser.add_argument('--recover-wallet-passphrase',
                        help="Passphrase of 12 words to recover and regenerate a previous wallet")

    pa = parser.parse_args()
    if pa.outputs_repeat and pa.outputs is None:
        parser.error("--output_repeat requires --outputs")
    if not pa.wallet_remove and not pa.list_wallets and not (pa.outputs or pa.outputs_import):
        parser.error("Either --outputs or --outputs-import should be specified")
    return pa

if __name__ == '__main__':
    # --- Parse commandline arguments ---
    args = parse_args()

    wallet_name = args.wallet_name
    network = args.network
    network_obj = Network(network)

    # List wallets, then exit
    if args.list_wallets:
        print("\nBitcoinlib wallets:")
        for w in list_wallets():
            print(w['name'])
        print("\n")
        sys.exit()

    # Delete specified wallet, then exit
    if args.wallet_remove:
        if not wallet_exists(args.wallet_remove):
            print("Wallet '%s' not found" % args.wallet_remove)
            sys.exit()
        inp = input("\nWallet '%s' with all keys and will be removed, without private key it cannot be restored."
                    "\nPlease retype exact name of wallet to proceed: " % args.wallet_remove)
        if inp == args.wallet_remove:
            print(delete_wallet(args.wallet_remove))
            print("\nWallet %s has been removed" % args.wallet_remove)
            sys.exit()

    # --- Create or open wallet ---
    if wallet_exists(wallet_name):
        wallet = BulkPaperWallet(wallet_name)
        if wallet.network.network_name != args.network:
            print("\nNetwork setting (%s) ignored. Using network from defined wallet instead: %s" %
                  (args.network, wallet.network.network_name))
            network = wallet.network.network_name
        print("\nOpen wallet '%s' (%s network)" % (wallet_name, network))
    else:
        print("\nCREATE wallet '%s' (%s network)" % (wallet_name, network))
        if not args.recover_wallet_passphrase:
            words = Mnemonic('english').generate()
            print("\nYour mnemonic private key sentence is: %s" % words)
            print("\nPlease write down on paper and backup. With this key you can restore all paper wallets if "
                  "something goes wrong during this process. You can / have to throw away this private key after "
                  "the paper wallets are distributed.")
            inp = input("\nType 'yes' if you understood and wrote down your key: ")
            if inp not in ['yes', 'Yes', 'YES']:
                print("Exiting...")
                sys.exit()
        else:
            words = args.recover_wallet_passphrase

        seed = binascii.hexlify(Mnemonic().to_seed(words))
        hdkey = HDKey().from_seed(seed, network=network)
        wallet = BulkPaperWallet.create(name=wallet_name, network=network, key=hdkey.wif())
        # wallet.new_account("Inputs", 0)
        wallet.new_key("Input", 0)
        wallet.new_account("Outputs", 1)

    # --- Create array with outputs ---
    if args.outputs_import:
        outputs = []
        # TODO: import amount and wallet names from csv
    else:
        outputs = [{'amount': o, 'name': ''} for o in args.outputs]

    outputs_arr = []
    output_keys = []
    total_amount = 0
    denominator = float(network_obj.denominator)
    for o in outputs:
        nk = wallet.new_key()
        output_keys.append(nk)
        amount = int(o['amount'] * (1/denominator))
        outputs_arr.append((nk.address, amount))
        total_amount += amount

    # --- Estimate transaction fees ---
    srv = Service(network=network)
    fee_per_byte = int(srv.estimatefee() / 1000)
    if not srv.results:
        raise ConnectionError("No response from services, could not determine estimated transaction fees")
    print(srv.results)
    estimated_fee = (200 + len(outputs_arr*50)) * fee_per_byte
    print("Estimated fee is for this transaction is %s" % network_obj.print_value(estimated_fee))
    print("Total value of outputs is %s" % network_obj.print_value(total_amount))
    total_transaction = total_amount + estimated_fee
    # if args.input_key:
    #     TODO write code to look for UTXO's

    # --- Check for UTXO's and create transaction and Paper wallets
    input_key = wallet.keys(name="Input")[0]
    wallet.updateutxos(0, input_key.id)
    input_key = wallet.keys(name="Input")[0]
    if input_key.balance < total_transaction:
        file_inputcode = os.path.join(WALLET_DIR, str(wallet.wallet_id) + '-input-address-qrcode.png')
        paymentlink = '%s:%s?amount=%.8f' % (network, input_key.address, total_transaction*denominator)
        ki_img = qrcode.make(paymentlink)
        ki_img.save(file_inputcode, 'PNG')
        print("\nNot enough funds in wallet to create transaction.\nPlease transfer %s to "
              "address %s and restart this program.\nYou can find a QR code in %s" %
              (network_obj.print_value(total_transaction - input_key.balance), input_key.address, file_inputcode))
    else:
        print("\nEnough input(s) to spent found, create wallets and transaction")
        t = wallet.create_transaction(outputs_arr, account_id=0, fee=estimated_fee, min_confirms=0)
        print("raw %s" % binascii.hexlify(t.raw()))
        wallet.create_paper_wallets(output_keys=output_keys)

        # TODO: Push transaction to network with Service class sendrawtransaction method

        # Transaction pushed to the network, txid: ...
        print("\nPaper wallets can be found in the %s directory" % WALLET_DIR)
