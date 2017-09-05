# -*- coding: iso-8859-15 -*-
#
# Bulk Paper Wallets
# Generate Bitcoin Paper Wallets in Bulk and fund them. Wallets will be saved as PDF files.
# © 2017 June - 1200 Web Development <http://1200wd.com/>
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
OUTPUT_ACCOUNT_ID = 1

pdfkit_options = {
    'page-size': 'A4',
    'margin-top': '0.25in',
    'margin-right': '0.25in',
    'margin-bottom': '0.25in',
    'margin-left': '0.25in',
    'encoding': "UTF-8",
}


class BulkPaperWallet(HDWallet):

    def create_paper_wallets(self, output_keys, style_file, template_file, image_size_factor=1):
        count = 0
        for wallet_key in output_keys:
            address_img = qrcode.make(wallet_key.address)
            filename_pre = "%s/%d-" % (WALLET_DIR, wallet_key.key_id)
            address_img.save(filename_pre+'address.png', 'PNG')

            private_wif = wallet_key.key().key.wif()
            priv_img = qrcode.make(private_wif)
            priv_img.save(filename_pre+'privatekey.png', 'PNG')

            f = open('templates/'+template_file, 'r')
            template = Template(f.read())
            wallet_name = "%s %d" % (self.name, wallet_key.key_id)
            wallet_str = template.render(
                install_dir=INSTALL_DIR,
                filename_pre=filename_pre,
                wallet_name=wallet_name,
                private_key=private_wif,
                address=wallet_key.address,
                currency_name=self.network.currency_name,
                currency_name_plural=self.network.currency_name_plural,
                image_size_factor=image_size_factor)
            print("Generate wallet %d" % wallet_key.key_id)
            pdfkit.from_string(wallet_str, filename_pre+'wallet.pdf', options=pdfkit_options, css=style_file)
            count += 1
        print("A total of %d paper wallets have been created" % count)

    @classmethod
    def create(cls, name, key='', owner='', network=None, account_id=0, purpose=44, databasefile=None):
        return super(BulkPaperWallet, cls).create(name=name, key=key, network=network, account_id=account_id,
                                                  purpose=purpose, databasefile=databasefile)


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
    parser.add_argument('--wallet-remove',
                        help="Name of wallet to remove, all keys and related information will be deleted")
    parser.add_argument('--list-wallets', '-l', action='store_true',
                        help="List all known wallets in bitcoinlib database")
    parser.add_argument('--wallet-info', '-i',
                        help="List all known wallets in bitcoinlib database")
    parser.add_argument('--recover-wallet-passphrase',
                        help="Passphrase of 12 words to recover and regenerate a previous wallet")
    parser.add_argument('--test-pdf', action='store_true',
                        help="Generate a single preview PDF paper wallet. Contains dummy keys")
    parser.add_argument('--style', '-s', default='style.css',
                        help="Specify style sheet file")
    parser.add_argument('--template', '-t', default='default.html',
                        help="Specify wallet template html file")
    parser.add_argument('--image-size', type=int, default=1,
                        help="Image size factor in paper wallets")
    parser.add_argument('--fee-per-kb', '-k', type=int,
                        help="Fee in satoshis per kilobyte")

    pa = parser.parse_args()
    if pa.outputs_repeat and pa.outputs is None:
        parser.error("--output_repeat requires --outputs")
    if not pa.wallet_remove and not pa.list_wallets and not pa.wallet_info and not pa.recover_wallet_passphrase \
            and not pa.test_pdf and not (pa.outputs or pa.outputs_import):
        parser.error("Either --outputs or --outputs-import should be specified")
    return pa

if __name__ == '__main__':
    # --- Parse commandline arguments ---
    args = parse_args()

    wallet_name = args.wallet_name
    network = args.network
    network_obj = Network(network)
    style_file = args.style
    template_file = args.template

    # List wallets, then exit
    if args.list_wallets:
        print("\nBitcoinlib wallets:")
        for w in list_wallets():
            print(w['name'])
        print("\n")
        sys.exit()

    if args.wallet_info:
        print("Wallet info for %s" % args.wallet_info)
        if wallet_exists(args.wallet_info):
            wallet = BulkPaperWallet(args.wallet_info)
            wallet.updateutxos()
            wallet.info()
        else:
            raise ValueError("Wallet '%s' not found" % args.wallet_info)
        sys.exit()

    # Delete specified wallet, then exit
    if args.wallet_remove:
        if not wallet_exists(args.wallet_remove):
            print("Wallet '%s' not found" % args.wallet_remove)
            sys.exit()
        inp = input("\nWallet '%s' with all keys and will be removed, without private key it cannot be restored."
                    "\nPlease retype exact name of wallet to proceed: " % args.wallet_remove)
        if inp == args.wallet_remove:
            if delete_wallet(args.wallet_remove, force=True):
                print("\nWallet %s has been removed" % args.wallet_remove)
            else:
                print("\nError when deleting wallet")
            sys.exit()

    # Generate a test wallet preview PDF
    if args.test_pdf:
        if wallet_exists('BPW_pdf_test_tmp'):
            wallet = BulkPaperWallet('BPW_pdf_test_tmp')
        else:
            wallet_obj = BulkPaperWallet
            wallet = wallet_obj.create(name='BPW_pdf_test_tmp', network=network)
        test_key = wallet.get_key()
        wallet.create_paper_wallets([test_key], style_file, template_file, args.image_size)

        delete_wallet('BPW_pdf_test_tmp')
        sys.exit()

    # --- Create or open wallet ---
    if wallet_exists(wallet_name):
        if args.recover_wallet_passphrase:
            print("\nWallet %s already exists. Please specify (not existing) wallet name for wallet to recover" %
                  wallet_name)
            sys.exit()
        wallet = BulkPaperWallet(wallet_name)
        if wallet.network.network_name != args.network:
            print("\nNetwork setting (%s) ignored. Using network from defined wallet instead: %s" %
                  (args.network, wallet.network.network_name))
            network = wallet.network.network_name
            network_obj = Network(network)
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
        wallet.new_key("Input")
        wallet.new_account("Outputs", account_id=OUTPUT_ACCOUNT_ID)

    if args.recover_wallet_passphrase:
        print("Wallet recovered, now updating keys and balances...")
        stuff_updated = True
        while stuff_updated:
            for kn in range(0, 10):
                wallet.new_key(account_id=OUTPUT_ACCOUNT_ID)
                wallet.new_key_change(account_id=OUTPUT_ACCOUNT_ID)
            stuff_updated = wallet.updateutxos()
        wallet.info()
        sys.exit()

    # --- Create array with outputs ---
    outputs = []
    if args.outputs_import:
        pass
        # TODO: import amount and wallet names from csv
    else:
        output_list = [{'amount': o, 'name': ''} for o in args.outputs]
        repeat_n = 1
        if args.outputs_repeat:
            repeat_n = args.outputs_repeat
        for r in range(0, repeat_n):
            outputs += output_list

    outputs_arr = []
    output_keys = []
    total_amount = 0
    denominator = float(network_obj.denominator)
    for o in outputs:
        nk = wallet.new_key(account_id=OUTPUT_ACCOUNT_ID)
        output_keys.append(nk)
        amount = int(o['amount'] * (1/denominator))
        outputs_arr.append((nk.address, amount))
        total_amount += amount

    # --- Estimate transaction fees ---
    srv = Service(network=network)
    if args.fee_per_kb:
        fee_per_kb = args.fee_per_kb
    else:
        fee_per_kb = srv.estimatefee()
        if not srv.results:
            raise IOError("No response from services, could not determine estimated transaction fees. "
                          "You can use --fee-per-kb option to determine fee manually and avoid this error.")
    tr_size = 100 + (1 * 150) + (len(outputs_arr) * 50)
    estimated_fee = int((tr_size / 1024) * fee_per_kb)
    if estimated_fee < 0:
        raise IOError("No valid response from any service provider, could not determine estimated transaction fees. "
                      "You can use --fee-per-kb option to determine fee manually and avoid this error.")
    print("Estimated fee is for this transaction is %s (%d satoshis/kb)" %
          (network_obj.print_value(estimated_fee), fee_per_kb))
    print("Total value of outputs is %s" % network_obj.print_value(total_amount))
    total_transaction = total_amount + estimated_fee

    # --- Check for UTXO's and create transaction and Paper wallets
    input_key = wallet.keys(name="Input")[0]
    wallet.updateutxos(0, input_key.id)
    print("\nTotal wallet balance: %s" % wallet.balance(fmt='string'))
    input_key = wallet.keys(name="Input")[0]
    if input_key.balance < total_transaction:
        remaining_balance = total_transaction - input_key.balance
        file_inputcode = os.path.join(WALLET_DIR, str(wallet.wallet_id) + '-input-address-qrcode.png')
        networklink = network
        if networklink == 'testnet':
            networklink = 'bitcoin'
        paymentlink = '%s:%s?amount=%.8f' % (networklink, input_key.address, remaining_balance*denominator)
        ki_img = qrcode.make(paymentlink)
        ki_img.save(file_inputcode, 'PNG')
        print("\nNot enough funds in wallet to create transaction.\nPlease transfer %s to "
              "address %s and restart this program with EXACTLY the same options.\nYou can find a QR code in %s" %
              (network_obj.print_value(remaining_balance), input_key.address, file_inputcode))
    else:
        print("\nEnough input(s) to spent found, ready to create wallets and transaction")
        if not args.template and not args.style:
            print("\nHave you created test-wallet PDFs to check page formatting with the '--test-pdf' option? "
                  "You can change font and image size with the --template and --style options")
        inp = input("\nType 'y' to continue: ")
        if inp not in ['y', 'Y']:
            print("Exiting...")
            sys.exit()
        wallet.create_paper_wallets(output_keys, style_file, template_file)
        tx_id = wallet.send(outputs_arr, account_id=0, transaction_fee=estimated_fee, min_confirms=0)

        print("\nTransaction pushed to the network, txid: %s" % tx_id)
        print("\nPaper wallets can be found in the %s directory" % WALLET_DIR)
