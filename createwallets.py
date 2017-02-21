# Bitcoins Uitdelen
# Doel: Scriptje om Bitcoins te verdelen over de keys van een wallet.
# Van elk van deze keys kan een print worden gemaakt van de private key.

import sys
import binascii
from bitcoinlib.wallets import HDWallet, delete_wallet
from bitcoinlib.keys import Key, HDKey
from bitcoinlib.transactions import Transaction, Input, Output
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.services.services import Service

# List of unspend transaction outputs to use as inputs
input_utxo = 'adee8bdd011f60e52949b65b069ff9f19fc220815fdc1a6034613ed1f6b775f1'
input_index = 0
input_pk = 'cRMjy1LLMPsVU4uaAt3br8Ft5vdJLx6prY4Sx7WjPARrpYAnVEkV'
# input_pk_byte = b'p\xae\xb538{\xa0}\x86\r &\xb5hl\xcb\x91\xca\xbb\x14\xd5\xb1\xab\x01\x06\x07\xa7\xbb\xbcH\xe7\xbd'

# Bitcoins uitdelen definitions
NETWORK = 'testnet'
WALLET_NAME = "Uitdelen"
OUTPUT_NUMBER = 5
OUTPUT_FEE = 10000
OUTPUT_AMOUNT = (135914715 / 5) - OUTPUT_FEE
PK_SENTENCE = 'dizzy shoe popular funny purse street drink jazz call key local movie'

# try:
#     delete_wallet(WALLET_NAME)
# except:
#     pass

# Create or open Wallet with Mnemonic Private HD Key
try:
    ew = HDWallet(WALLET_NAME)
except:
    if not PK_SENTENCE:
        words = Mnemonic('english').generate()
        print("Your mnemonic private key sentence is: %s" % words)
        print("\nPlease write down on paper and backup. IF YOU LOSE THIS PRIVATE KEY ALL COINS ARE LOST!")
        inp = raw_input("Type 'yes' if you understood and wrote down your key: ")
        if inp not in ['yes', 'Yes', 'YES']:
            print("Exiting...")
            sys.exit()
    else:
        words = PK_SENTENCE

    seed = binascii.hexlify(Mnemonic().to_seed(words))
    hdkey = HDKey().from_seed(seed, network=NETWORK)
    ew = HDWallet.create(name=WALLET_NAME, network=NETWORK, key=hdkey.extended_wif())

    # Add Transaction Input
    ki = Key(input_pk)
    print(ki.wif())
    inputs = [Input(input_utxo, input_index, public_key=ki.public_byte(), network=NETWORK)]

    # Add Transaction Outputs
    outputs = []
    for _ in range(0, OUTPUT_NUMBER):
        nk = ew.new_key()
        outputs.append(Output(OUTPUT_AMOUNT, address=nk.address, network=NETWORK))

    t = Transaction(inputs=inputs, outputs=outputs, network=NETWORK)

    from pprint import pprint
    t.sign(ki.private_byte(), 0)
    print(binascii.hexlify(t.raw()))
    pprint(t.get())
    print("Verified %s " % t.verify())
    print(binascii.hexlify(t.raw()))

    ew.updatebalance()
    ew.updateutxos()

inputs = []
for dbkey in ew.keys_addresses(account_id=0):
    pk = HDKey(dbkey.key_wif)
    utxo = Service(network='testnet').getutxos(dbkey.address)[0]
    prev_hash = utxo['tx_hash']
    output_n = utxo['output_n']
    print(prev_hash, output_n, pk.private().wif())
    inputs.append(Input(prev_hash, output_n, public_key=pk.public().public_byte(), network=NETWORK))

outputs = [Output(135860000, address='mkzpsGwaUU7rYzrDZZVXFne7dXEeo6Zpw2', network='testnet')]
t = Transaction(inputs, outputs, network='testnet')
print(t.get())
print(binascii.hexlify(t.rawtx))


