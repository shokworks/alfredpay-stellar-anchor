import os
import toml
from urllib.parse import urlparse

from django.utils.translation import gettext

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from polaris import settings
from polaris.integrations import registered_toml_func
from polaris.models import Asset
from polaris.utils import getLogger, render_error_response
from polaris.sep1.views import PolarisPlainTextRenderer, generate_toml
from polaris.sep10.views import SEP10Auth

from stellar_sdk import Keypair
from stellar_sdk.client.requests_client import RequestsClient
from stellar_sdk.sep.stellar_toml import fetch_stellar_toml
from stellar_sdk.operation import ManageData

from stellar_sdk.sep.exceptions import (
    InvalidSep10ChallengeError,
    StellarTomlNotFoundError,
)
from .stellar_web_authentication import (
    build_challenge_transaction,
    read_challenge_transaction,
    verify_challenge_transaction_threshold,
    verify_challenge_transaction_signed_by_client_master_key,
)

MIME_URLENCODE, MIME_JSON = "application/x-www-form-urlencoded", "application/json"
logger = getLogger(__name__)

@api_view(["GET", "HEAD"])
@renderer_classes([PolarisPlainTextRenderer])
def generate_toml(generate_toml):
    toml_dict1 = {
        "VERSION": "0.1.1",
    }
    toml_dict2 = {
        "NETWORK_PASSPHRASE": settings.STELLAR_NETWORK_PASSPHRASE,
        "WEB_AUTH_ENDPOINT": os.path.join(settings.HOST_URL, "auth"),
        "SIGNING_KEY": settings.SIGNING_KEY,
        "TRANSFER_SERVER": os.path.join(settings.HOST_URL, "sep24"),
        "TRANSFER_SERVER_SEP0024": os.path.join(settings.HOST_URL, "sep24"),
        "ACCOUNTS": [
            asset.distribution_account
            for asset in Asset.objects.exclude(distribution_seed__isnull=True)
        ],
        "DOCUMENTATION": {
            "ORG_NAME": "Alfred Pay",
            "ORG_DBA": "Alfred Payment Solutions",
<<<<<<< HEAD
            "ORG_URL": "https://alfredpay.io",
=======
            "ORG_URL": "alfredpay.io",
>>>>>>> 6d01b5c91b52143831b09596c6d4b63141490247
            "ORG_LOGO": "https://alfred-pay.com/wp-content/themes/Alfred%20Pay%20Theme/assets/images/Logo_Alfred.svg",
            "ORG_DESCRIPTION": "Cross border remittance platform on the stellar blockchain that uses USDC as a medium of exchange.",
            "ORG_PHYSICAL_ADDRESS": "7440 N Kendall Dr unit 1806 Miami FL 33156",
            "ORG_PHONE_NUMBER": "1 (786)-374-4251",
            "ORG_TWITTER": "@alfredpayapp",
            "ORG_OFFICIAL_EMAIL": "hello@alfred-pay.com",
        },
    }
    toml_dict3 = {
        "CURRENCIES": [
<<<<<<< HEAD
            {"code": asset.code, "issuer": asset.issuer,
	    "status": "test", "is_asset_anchored": False,
	    "anchor_asset_type": "fiat",
	    "desc": "Cross border remittance anchor that uses USDC as a medium of exchange."}
=======
            {"code": asset.code, "issuer": asset.issuer}
>>>>>>> 6d01b5c91b52143831b09596c6d4b63141490247
            for asset in Asset.objects.all().iterator()
        ],
    }
    content = toml.dumps(toml_dict1) + "\n" + toml.dumps(toml_dict2) + "\n" + toml.dumps(toml_dict3)

    return Response(content, content_type="text/plain")

# if hasattr(self, 'get') and not hasattr(self, 'head'):
#     self.head = self.get


class MySEP10Auth(SEP10Auth):

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, *_args, **_kwargs) -> Response:
        account = request.GET.get("account")
        if not account:
            return Response(
                {"error": "no 'account' provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        home_domain = request.GET.get("home_domain")
        if home_domain and home_domain not in settings.SEP10_HOME_DOMAINS:
            return Response(
                {
                    "error": f"invalid 'home_domain' value. Accepted values: {settings.SEP10_HOME_DOMAINS}"}, status=status.HTTP_400_BAD_REQUEST,)
        elif not home_domain:
            home_domain = settings.SEP10_HOME_DOMAINS[0]

        client_domain, client_signing_key = request.GET.get("client_domain"), None
        if settings.SEP10_CLIENT_ATTRIBUTION_REQUIRED and not client_domain:
            return render_error_response(
                gettext("'client_domain' is required"), status_code=400
            )
        elif client_domain:
            if urlparse(f"https://{client_domain}").netloc != client_domain:
                return render_error_response(
                    gettext("'client_domain' must be a valid hostname"), status_code=400
                )
            elif (
                settings.SEP10_CLIENT_ATTRIBUTION_DENYLIST
                and client_domain in settings.SEP10_CLIENT_ATTRIBUTION_DENYLIST
            ) or (
                settings.SEP10_CLIENT_ATTRIBUTION_ALLOWLIST
                and client_domain not in settings.SEP10_CLIENT_ATTRIBUTION_ALLOWLIST
            ):
                if settings.SEP10_CLIENT_ATTRIBUTION_REQUIRED:
                    return render_error_response(
                        gettext("unrecognized 'client_domain'"), status_code=403
                    )
                else:
                    client_domain = None

        if client_domain:
            try:
                client_signing_key = self._get_client_signing_key(client_domain)
            except (
                ConnectionError,
                StellarTomlNotFoundError,
                toml.decoder.TomlDecodeError,
            ):
                return render_error_response(
                    gettext("unable to fetch 'client_domain' SIGNING_KEY"),
                )
            except ValueError as e:
                return render_error_response(str(e))

        try:
            transaction = self._challenge_transaction(
                account, home_domain, client_domain, client_signing_key
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        print(f"transaction: {transaction}")
        return Response(
            {
                "transaction": transaction,
                "network_passphrase": settings.STELLAR_NETWORK_PASSPHRASE,
            }
        )

    @staticmethod
    def _get_client_signing_key(client_domain):
<<<<<<< HEAD
        client_toml_contents = fetch_stellar_toml(
            client_domain,
            use_http=False,
=======
        print(f"PASO 7 client_signing_key = self._get_client_signing_key(client_domain): True")
        print(f"NOTA fetch_stellar_toml ESTA USANDO use_http=True PARA PRUEBAS SIN SSL")
        client_toml_contents = fetch_stellar_toml(
            client_domain,
            use_http=True,
>>>>>>> 6d01b5c91b52143831b09596c6d4b63141490247
            client=RequestsClient(
                request_timeout=settings.SEP10_CLIENT_ATTRIBUTION_REQUEST_TIMEOUT
            ),
        )
        client_signing_key = client_toml_contents.get("SIGNING_KEY")
        if not client_signing_key:
            raise ValueError(gettext("SIGNING_KEY not present on 'client_domain' TOML"))
        try:
            Keypair.from_public_key(client_signing_key)
        except Ed25519PublicKeyInvalidError:
            raise ValueError(
                gettext("invalid SIGNING_KEY value on 'client_domain' TOML")
            )
        return client_signing_key

    def post(self, request: Request, *_args, **_kwargs) -> Response:
        envelope_xdr = request.data.get("transaction")
        if not envelope_xdr:
            return render_error_response(gettext("'transaction' is required"))
        client_domain, error_response = self._validate_challenge_xdr(envelope_xdr)
        if error_response:
            return error_response
        else:
            return Response({"token": self._generate_jwt(envelope_xdr, client_domain)})

    @staticmethod
    def _validate_challenge_xdr(envelope_xdr: str):
        logger.info("Validating challenge transaction")
        generic_err_msg = gettext("error while validating challenge: %s")
        try:
            challenge = read_challenge_transaction(
                challenge_transaction=envelope_xdr,
                server_account_id=settings.SIGNING_KEY,
                home_domains=settings.SEP10_HOME_DOMAINS,
                web_auth_domain=urlparse(settings.HOST_URL).netloc,
                network_passphrase=settings.STELLAR_NETWORK_PASSPHRASE,
            )
        except (InvalidSep10ChallengeError, TypeError) as e:
            return None, render_error_response(generic_err_msg % (str(e)))

        client_domain = None
        for operation in challenge.transaction.transaction.operations:
            if (
                isinstance(operation, ManageData)
                and operation.data_name == "client_domain"
            ):
                client_domain = operation.data_value.decode()
                break

        try:
            account = settings.HORIZON_SERVER.load_account(challenge.client_account_id)
        except NotFoundError:
            logger.info("Account does not exist, using client's master key to verify")
            try:
                verify_challenge_transaction_signed_by_client_master_key(
                    challenge_transaction=envelope_xdr,
                    server_account_id=settings.SIGNING_KEY,
                    home_domains=settings.SEP10_HOME_DOMAINS,
                    web_auth_domain=urlparse(settings.HOST_URL).netloc,
                    network_passphrase=settings.STELLAR_NETWORK_PASSPHRASE,
                )
                if (client_domain and len(challenge.transaction.signatures) != 3) or (
                    not client_domain and len(challenge.transaction.signatures) != 2
                ):
                    raise InvalidSep10ChallengeError(
                        gettext(
                            "There is more than one client signer on a challenge "
                            "transaction for an account that doesn't exist"
                        )
                    )
            except InvalidSep10ChallengeError as e:
                logger.info(
                    f"Missing or invalid signature(s) for {challenge.client_account_id}: {str(e)}"
                )
                return None, render_error_response(generic_err_msg % (str(e)))
            else:
                logger.info("Challenge verified using client's master key")
                return client_domain, None

        signers = account.load_ed25519_public_key_signers()
        threshold = account.thresholds.med_threshold
<<<<<<< HEAD
=======
        print(f"threshold = account.thresholds.med_threshold: {threshold}")
>>>>>>> 6d01b5c91b52143831b09596c6d4b63141490247
        try:
            signers_found = verify_challenge_transaction_threshold(
                challenge_transaction=envelope_xdr,
                server_account_id=settings.SIGNING_KEY,
                home_domains=settings.SEP10_HOME_DOMAINS,
                web_auth_domain=urlparse(settings.HOST_URL).netloc,
                network_passphrase=settings.STELLAR_NETWORK_PASSPHRASE,
                threshold=threshold,
                signers=signers,
            )
        except InvalidSep10ChallengeError as e:
            return None, render_error_response(generic_err_msg % (str(e)))

        logger.info(
            f"Challenge verified using account signers: {[s.account_id for s in signers_found]}"
        )
        return client_domain, None
<<<<<<< HEAD
=======

>>>>>>> 6d01b5c91b52143831b09596c6d4b63141490247
