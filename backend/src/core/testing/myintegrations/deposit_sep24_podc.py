from stellar_sdk import (
    Keypair, Network, Server, TransactionBuilder
)


server = Server(horizon_url="https://horizon-testnet.stellar.org")
distributor_secret_key = "SDHQXUK5NJE7Z2RGJ4CWU22WGHBCFGIKAH4MGVZ45AK76M4UHBATRVGP"
distributor_public = Keypair.from_secret(distributor_secret_key).public_key
distributor_account = server.load_account(distributor_public)

def get_change_trust_op(asset_code, destination):
    transaction1 = (
        TransactionBuilder(
            source_account=distributor_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_change_trust_op(
            asset_code=asset_code,
            asset_issuer=destination,
            limit=None
            )
        .set_timeout(30)
        .build()
    )
    transaction1.sign(distributor_secret_key)
    response1 = server.submit_transaction(transaction1)
    return response1

def get_payment_op(asset_code, destination, amount):
    transaction2 = (
        TransactionBuilder(
            source_account=distributor_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_payment_op(
            destination=destination,
            amount=amount,
            asset_code=asset_code,
            asset_issuer=distributor_public
            )
        .set_timeout(30)
        .build()
    )
    transaction2.sign(distributor_secret_key)
    response2 = server.submit_transaction(transaction2)
    return transaction2, response2
