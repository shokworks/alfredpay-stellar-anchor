from stellar_sdk.sep.txrep import from_txrep, to_txrep
from stellar_sdk import (
    Asset, Keypair, Network, Server, TransactionBuilder
)


def sep6_deposit(asset_code, destination, amount):
    server = Server(horizon_url="https://horizon-testnet.stellar.org")
    distributor_secret_key = "SCYZ5ND7X7IUX3AD2VE7QIEF5Z5ARWLWV6X2ZXDSEXUJWYOWSWMPMEG5"
    distributor_keypair = Keypair.from_secret(distributor_secret_key)
    distributor_public = distributor_keypair.public_key
    distributor_account = server.load_account(distributor_public)
    n_asset = Asset('PODC', distributor_public)
    transaction1 = (
        TransactionBuilder(
            source_account=distributor_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_change_trust_op(asset=n_asset)
        .set_timeout(30)
        .build()
    )
    transaction1.sign(distributor_secret_key)

    distributor_account = server.load_account(distributor_public)
    transaction2 = (
        TransactionBuilder(
            source_account=distributor_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        # .append_change_trust_op(asset=n_asset)
        # .append_payment_op(destination, Asset('PODC', distributor_public), "350.1234567")
        .append_payment_op(
            destination=destination,
            amount=amount,
            asset=n_asset
            )
        .set_timeout(30)
        .build()
    )
    transaction2.sign(distributor_secret_key)
    # try:
    #     response1 = server.submit_transaction(transaction1)
    # except:
    #     pass
    response2 = server.submit_transaction(transaction2)
    return transaction2, response2

    # print(f"transaction1: {to_txrep(transaction1)}")

