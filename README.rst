Bulk Paper Wallets
==================

Create Bulk Bitcoin Paper Wallets

* Generate infinite paper wallets
* Possible to use different amounts for each wallet (via commandline or CSV import)
* Possible to use an offline computer
* Derives all private keys for wallet from one masterkey. So you will be able to restore a wallet if someone
  lost his wallet. Off course this has some security and trust implications.
* Uses easy to design Jinja2 template. Use default one provided or update to your own needs


Installation
------------

Uses the bitcoinlib Bitcoin Library

``pip install bitcoinlib``

And libraries to generate PDF paper wallets with Jinja template markup and QR code's

``pip install qrcode pdfkit jinja2``

And the libraries to generate a PDF from HTML
(see https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf for other OS):

``apt install wkhtmltopdf``

And if you get PIL or Image errors

``pip install image``


Usage reference
---------------

Use from commandline with python

.. code-block:: bash

    usage: createwallets.py [-h] [--wallet-name WALLET_NAME] [--network NETWORK]
                        [--outputs [OUTPUTS [OUTPUTS ...]] | --outputs-import
                        OUTPUTS_IMPORT] [--outputs-repeat OUTPUTS_REPEAT]
                        [--wallet-remove WALLET_REMOVE] [--list-wallets]
                        [--recover-wallet-passphrase RECOVER_WALLET_PASSPHRASE]

    optional arguments:

          -h, --help            show this help message and exit
          --wallet-name WALLET_NAME, -w WALLET_NAME
                                Name of wallet to create or open. Used to store your
                                all your wallet keys and will be printed on each paper
                                wallet
          --network NETWORK, -n NETWORK
                                Specify 'bitcoin', 'testnet' or other supported
                                network
          --outputs [OUTPUTS [OUTPUTS ...]], -o [OUTPUTS [OUTPUTS ...]]
                                List of output values. For example '-o 1 2 3' creates
                                3 wallets with a value of 1, 2 and 3 bitcoin
                                successively
          --outputs-import OUTPUTS_IMPORT, -f OUTPUTS_IMPORT
                                Filename of comma seperated value list of output
                                values and optional wallet names. Example: 1.51, John
          --outputs-repeat OUTPUTS_REPEAT, -r OUTPUTS_REPEAT
                                Repeat the outputs OUTPUTS_REPEAT times. For example
                                'createwallet.py -o 5 -r 10' will create 10 wallets
                                with 5 bitcoin
          --wallet-remove WALLET_REMOVE
                                Name of wallet to remove, all keys and related
                                information will be deleted
          --list-wallets, -l    List all known wallets in bitcoinlib database
          --recover-wallet-passphrase RECOVER_WALLET_PASSPHRASE
                                Passphrase of 12 words to recover and regenerate a
                                previous wallet


Example: Create paper wallets
-----------------------------

Create 2 paper wallets with 0.01 bitcoin and 0.001 bitcoin:

.. code-block:: bash

    $ python createwallets.py -o 0.001 0.01
    
    CREATE wallet 'Bulk Paper Wallet' (bitcoin network)
    
    Your mnemonic private key sentence is: tide dirt obscure round demand engine nominee destroy swamp smile board decrease

    Please write down on paper and backup. With this key you can restore all paper wallets if something goes wrong
    during this process. You can / have to throw away this private key after the paper wallets are distributed.

    Type 'yes' if you understood and wrote down your key: 


Now write down the private key sentence on a piece of paper and confirm

.. code-block:: bash

    Estimated fee is for this transaction is 0.00060000 BTC
    Total value of outputs is 0.01100000 BTC

    Not enough funds in wallet to create transaction.
    Please transfer 0.01160000 BTC to address 1Cg7pnT1Ympu4LnmF3s58VEnRhAJZjLnRK and restart this program.
    You can find a QR code in wallets/8-input-address-qrcode.png


Copy-n-paste the address or scan the QR code with your favorite wallet and send the coins.

Restart the program with the same options:

.. code-block:: bash

    $ python createwallets.py -o 0.001 0.01

    Open wallet 'Bulk Paper Wallet' (bitcoin network)
    Estimated fee is for this transaction is 0.00060000 BTC
    Total value of outputs is 0.01100000 BTC

    Enough input(s) to spent found, create wallets and transaction
    Raw Transaction: raw b'010000000 .... 88ac00000000'

    Generate wallet 74
    Loading page (1/2)
    Printing pages (2/2)                                               
    Done                                                           
    Generate wallet 75
    Loading page (1/2)
    Printing pages (2/2)                                               
    Done                                                           
    A total of 2 paper wallets have been created

    Transaction pushed to the network, txid: 0177ac29fa8b2960051321c730c6f15017503aa5b9c1dd2d61e7286e366fbaba
    Paper wallets can be found in the wallets directory


Paper wallets are now funded and ready to use. Print and store in a safe location.


