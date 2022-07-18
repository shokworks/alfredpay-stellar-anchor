import os
import environ
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from stellar_sdk.sep.txrep import from_txrep, to_txrep
from stellar_sdk import (
    Asset, Keypair, Network, Server, TransactionBuilder
)


SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '../../'))

env = environ.Env()
env_file = os.path.abspath(os.path.join(BASE_DIR, 'etc/.env'))

try:
    os.path.exists(env_file)
    environ.Env.read_env(env_file)
except KeyError:
    raise ImproperlyConfigured(f"Problems with the {env_file} file")

SIGNING_SEED = env("SIGNING_SEED")
SIGNER_SEED_TWO = env("SIGNER_SEED_TWO")


def sep6_deposit(asset_code, amount):
    server = Server(horizon_url="https://horizon-testnet.stellar.org")

    servidor_secret_key = SIGNING_SEED
    servidor_keypair = Keypair.from_secret(servidor_secret_key)
    servidor_public = servidor_keypair.public_key
    servidor_account = server.load_account(servidor_public)

    cliente_secret_key = SIGNER_SEED_TWO
    cliente_keypair = Keypair.from_secret(cliente_secret_key)
    cliente_public = cliente_keypair.public_key
    cliente_account = server.load_account(cliente_public)

    transaction1 = (
        TransactionBuilder(
            source_account=cliente_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_change_trust_op(asset=Asset(asset_code, servidor_public))
        .set_timeout(30)
        .build()
    )
    transaction1.sign(cliente_secret_key)
    response1 = server.submit_transaction(transaction1)
    print(response1)

    transaction2 = (
        TransactionBuilder(
            source_account=servidor_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_payment_op(
            destination=cliente_public,
            amount=amount,
            asset=Asset(asset_code, servidor_public)
            )
        .set_timeout(30)
        .build()
    )
    transaction2.sign(servidor_secret_key)
    response2 = server.submit_transaction(transaction2)
    print(f"\n\n\n\n\n")
    print(response2)
    return transaction2, response2