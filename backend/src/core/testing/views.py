import os
import jwt
import toml
from urllib.parse import urlparse

from django.http import HttpResponseRedirect
from django.contrib.staticfiles import finders
from django.shortcuts import render
from django.utils.encoding import smart_str
from django.utils.translation import gettext
from django.views.generic import View

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView

from stellar_sdk import Keypair
from stellar_sdk.client.requests_client import RequestsClient
from stellar_sdk.operation import ManageData
from stellar_sdk.exceptions import (
    NotFoundError,
    ConnectionError,
    Ed25519PublicKeyInvalidError,
)
from stellar_sdk.sep.exceptions import (
    InvalidSep10ChallengeError,
    StellarTomlNotFoundError,
)
from stellar_sdk.sep.stellar_toml import fetch_stellar_toml

from core.polaris import settings
from core.polaris.integrations import registered_toml_func, get_stellar_toml
from core.polaris.models import Asset
from core.polaris.utils import getLogger, render_error_response
from core.polaris.sep1.views import PolarisPlainTextRenderer, generate_toml
from core.polaris.sep10.views import SEP10Auth

from core.testing.stellar_web_authentication import (
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
        "ACCOUNTS": [
            asset.distribution_account
            for asset in Asset.objects.exclude(distribution_seed__isnull=True)
        ],
        "DOCUMENTATION": {
            "ORG_NAME": "Alfred Pay",
            "ORG_DBA": "Alfred Payment Solutions",
            "ORG_URL": "https://alfredpay.io",
            "ORG_LOGO": "https://alfred-pay.com/wp-content/themes/Alfred%20Pay%20Theme/assets/images/Logo_Alfred.svg",
            "ORG_DESCRIPTION": "Cross border remittance platform on the stellar blockchain that uses USDC as a medium of exchange.",
            "ORG_PHYSICAL_ADDRESS": "7440 N Kendall Dr unit 1806 Miami FL 33156",
            "ORG_PHONE_NUMBER": "1 (786)-374-4251",
            "ORG_TWITTER": "@alfredpayapp",
            "ORG_OFFICIAL_EMAIL": "hello@alfred-pay.com",
        },
    }
    if "sep-24" in settings.ACTIVE_SEPS:
        toml_dict2["TRANSFER_SERVER"] = os.path.join(settings.HOST_URL, "sep24")
        toml_dict2["TRANSFER_SERVER_SEP0024"] = toml_dict2["TRANSFER_SERVER"]
    if "sep-6" in settings.ACTIVE_SEPS:
        toml_dict2["TRANSFER_SERVER"] = os.path.join(settings.HOST_URL, "sep6")
    if "sep-10" in settings.ACTIVE_SEPS:
        toml_dict2["WEB_AUTH_ENDPOINT"] = os.path.join(settings.HOST_URL, "auth")
        toml_dict2["SIGNING_KEY"] = settings.SIGNING_KEY
    if "sep-12" in settings.ACTIVE_SEPS:
        toml_dict2["KYC_SERVER"] = os.path.join(settings.HOST_URL, "kyc")
    if "sep-31" in settings.ACTIVE_SEPS:
        toml_dict2["DIRECT_PAYMENT_SERVER"] = os.path.join(settings.HOST_URL, "sep31")

    currencies = []
    for asset in Asset.objects.all().iterator():
        if asset.code == "USDC":
            currencies1 = {
                "code": asset.code, "issuer": asset.issuer,
                "status": "test", "is_asset_anchored": True,
                "anchor_asset_type": "fiat", "anchor_asset": "USD", "name": "USD Coin",
                "redemption_instructions": "Redeemable through a Alfred-pay account at https://alfredpay.io",
                "desc": "Cross border remittance anchor that uses USDC as a medium of exchange."
            }
            currencies.append(currencies1)
        elif asset.code == "PODC":
            currencies1b = {
                "code": asset.code, "issuer": asset.issuer,
                "status": "test", "is_asset_anchored": True,
                "anchor_asset_type": "fiat", "anchor_asset": "POD", "name": "POD Coin",
                "redemption_instructions": "Redeemable through a Alfred-pay account at https://alfredpay.io",
                "desc": "Cross border remittance anchor that uses PODC as a medium of exchange."
            }
            currencies.append(currencies1b)
        else:
            currencies2 = {"code": asset.code, "issuer": asset.issuer,
                           "status": "test", "is_asset_anchored": False}
            currencies.append(currencies2)
    toml_dict3 = {}
    toml_dict3["CURRENCIES"] = []
    toml_dict3.update({"CURRENCIES": currencies})

    content = toml.dumps(toml_dict1) + "\n" + toml.dumps(toml_dict2) + "\n" + toml.dumps(toml_dict3)

    return Response(content, content_type="text/plain")

# if hasattr(self, 'get') and not hasattr(self, 'head'):
#     self.head = self.get


class MySEP10Auth(SEP10Auth):

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    ###############
    # GET functions
    ###############
    def get(self, request, *_args, **_kwargs) -> Response:
        account = request.GET.get("account")
        if not account:
            return Response(
                {"error": "no 'account' provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        memo = request.GET.get("memo")
        if memo:
            try:
                memo = int(memo)
            except ValueError:
                return Response(
                    {"error": "invalid 'memo' value. Expected a 64-bit integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if account.startswith("M"):
                return Response(
                    {
                        "error": "'memo' cannot be passed with a muxed client account address (M...)"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        home_domain = request.GET.get("home_domain")
        if home_domain and home_domain not in settings.SEP10_HOME_DOMAINS:
            return Response(
                {
                    "error": f"invalid 'home_domain' value. Accepted values: {settings.SEP10_HOME_DOMAINS}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
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
                account, home_domain, client_domain, client_signing_key, memo
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Returning SEP-10 challenge for account {account}")
        return Response(
            {
                "transaction": transaction,
                "network_passphrase": settings.STELLAR_NETWORK_PASSPHRASE,
            }
        )

    @staticmethod
    def _challenge_transaction(
        client_account,
        home_domain,
        client_domain=None,
        client_signing_key=None,
        memo=None,
    ):
        """
        Generate the challenge transaction for a client account.
        This is used in `GET <auth>`, as per SEP 10.
        Returns the XDR encoding of that transaction.
        """
        return build_challenge_transaction(
            server_secret=settings.SIGNING_SEED,
            client_account_id=client_account,
            home_domain=home_domain,
            web_auth_domain=urlparse(settings.HOST_URL).netloc,
            network_passphrase=settings.STELLAR_NETWORK_PASSPHRASE,
            timeout=900,
            client_domain=client_domain,
            client_signing_key=client_signing_key,
            memo=memo,
        )

    ################
    # POST functions
    ################
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
        """
        Validate the provided TransactionEnvelope XDR (base64 string).

        If the source account of the challenge transaction exists, verify the weight
        of the signers on the challenge are signers for the account and the medium
        threshold on the account is met by those signers.

        If the source account does not exist, verify that the keypair used as the
        source for the challenge transaction has signed the challenge. This is
        sufficient because newly created accounts have their own keypair as signer
        with a weight greater than the default thresholds.
        """
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

        # extract the Stellar account from the muxed account to check for its existence
        stellar_account = challenge.client_account_id
        if challenge.client_account_id.startswith("M"):
            stellar_account = MuxedAccount.from_account(
                challenge.client_account_id
            ).account_id

        try:
            account = settings.HORIZON_SERVER.load_account(stellar_account)
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

    @staticmethod
    def _generate_jwt(envelope_xdr: str, client_domain: str = None) -> str:
        """
        Generates the JSON web token from the challenge transaction XDR.

        See: https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0010.md#token
        """
        challenge = read_challenge_transaction(
            challenge_transaction=envelope_xdr,
            server_account_id=settings.SIGNING_KEY,
            home_domains=settings.SEP10_HOME_DOMAINS,
            web_auth_domain=urlparse(settings.HOST_URL).netloc,
            network_passphrase=settings.STELLAR_NETWORK_PASSPHRASE,
        )
        logger.info(
            f"Generating SEP-10 token for account {challenge.client_account_id}"
        )

        # set iat value to minimum timebound of the challenge so that the JWT returned
        # for a given challenge is always the same.
        # https://github.com/stellar/stellar-protocol/pull/982
        issued_at = challenge.transaction.transaction.preconditions.time_bounds.min_time

        # format sub value based on muxed account or memo
        if challenge.client_account_id.startswith("M") or not challenge.memo:
            sub = challenge.client_account_id
        else:
            sub = f"{challenge.client_account_id}:{challenge.memo}"

        jwt_dict = {
            "iss": os.path.join(settings.HOST_URL, "auth"),
            "sub": sub,
            "iat": issued_at,
            "exp": issued_at + 24 * 60 * 60,
            "jti": challenge.transaction.hash().hex(),
            "client_domain": client_domain,
        }
        return jwt.encode(jwt_dict, settings.SERVER_JWT_KEY, algorithm="HS256")

    @staticmethod
    def _get_client_signing_key(client_domain):
        client_toml_contents = fetch_stellar_toml(
            client_domain,
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

        return Response(
            {
                "transaction": transaction,
                "network_passphrase": settings.STELLAR_NETWORK_PASSPHRASE,
            }
        )

    @staticmethod
    def _get_client_signing_key(client_domain):
        client_toml_contents = fetch_stellar_toml(
            client_domain,
            use_http=False,
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


class get_home(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pruebas/home.html')
