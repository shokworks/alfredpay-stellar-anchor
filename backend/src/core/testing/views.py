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
from stellar_sdk.sep.exceptions import (
    InvalidSep10ChallengeError,
    StellarTomlNotFoundError,
)

MIME_URLENCODE, MIME_JSON = "application/x-www-form-urlencoded", "application/json"
logger = getLogger(__name__)

@api_view(["GET"])
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
            "ORG_NAME": "Organization Name",
            "ORG_DBA": "Organization DBA",
            "ORG_URL": "https://www.domain.com",
            "ORG_LOGO": "https://www.domain.com/awesomelogo.png",
            "ORG_DESCRIPTION": "Description of issuer",
            "ORG_PHYSICAL_ADDRESS": "address of company",
            "ORG_PHYSICAL_ADDRESS_ATTESTATION": "https://www.domain.com/address_attestation.jpg",
            "ORG_PHONE_NUMBER": "1 (123)-456-7890",
            "ORG_PHONE_NUMBER_ATTESTATION": "https://www.domain.com/phone_attestation.jpg",
            "ORG_KEYBASE": "accountname",
            "ORG_TWITTER": "orgtweet",
            "ORG_GITHUB": "orgcode",
            "ORG_OFFICIAL_EMAIL": "support@domain.com",
        },
        "PRINCIPALS": {
            "name": "Soporte Tecnico",
            "email": "jane@domain.com",
            "keybase": "crypto_soporte",
            "twitter": "crypto_soporte",
            "github": "crypto_soporte",
        },
    }
    toml_dict3 = {
        "CURRENCIES": [
            {"code": asset.code, "issuer": asset.issuer}
            for asset in Asset.objects.all().iterator()
        ],
    }
    content = toml.dumps(toml_dict1) + "\n" + toml.dumps(toml_dict2) + "\n" + toml.dumps(toml_dict3)

    return Response(content, content_type="text/plain")

class MySEP10Auth(SEP10Auth):

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, *_args, **_kwargs) -> Response:
        print(f"\n\n\n\n\n\n\n")
        account = request.GET.get("account")
        # print(f"PASO 1 account: {account}")
        if not account:
            return Response(
                {"error": "no 'account' provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        home_domain = request.GET.get("home_domain")
        # print(f"PASO 2 request.GET.get('home_domain'): {home_domain}")
        if home_domain and home_domain not in settings.SEP10_HOME_DOMAINS:
            # print(f"PASO 3 settings.SEP10_HOME_DOMAINS: {settings.SEP10_HOME_DOMAINS}")
            # print(f"PASO 4 Error: invalid 'home_domain' value.")
            return Response(
                {
                    "error": f"invalid 'home_domain' value. Accepted values: {settings.SEP10_HOME_DOMAINS}"}, status=status.HTTP_400_BAD_REQUEST,)
        elif not home_domain:
            home_domain = settings.SEP10_HOME_DOMAINS[0]
            # print(f"PASO 5 elif not home_domain: True")
            # print(f"home_domain = settings.SEP10_HOME_DOMAINS[0]: {home_domain}")

        client_domain, client_signing_key = request.GET.get("client_domain"), None
        # print(f"PASO 6 settings.SEP10_CLIENT_ATTRIBUTION_REQUIRED: {settings.SEP10_CLIENT_ATTRIBUTION_REQUIRED}")
        # print(f"client_domain = request.GET.get('client_domain'): {client_domain}")
        # print(f"client_signing_key: {client_signing_key}")
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
        print(f"\n\n")
        return Response(
            {
                "transaction": transaction,
                "network_passphrase": settings.STELLAR_NETWORK_PASSPHRASE,
            }
        )

    @staticmethod
    def _get_client_signing_key(client_domain):
        print(f"PASO 7 client_signing_key = self._get_client_signing_key(client_domain): True")
        print(f"NOTA fetch_stellar_toml ESTA USANDO use_http=True PARA PRUEBAS SIN SSL")
        client_toml_contents = fetch_stellar_toml(
            client_domain,
            use_http=True,
            client=RequestsClient(
                request_timeout=settings.SEP10_CLIENT_ATTRIBUTION_REQUEST_TIMEOUT
            ),
        )
        client_signing_key = client_toml_contents.get("SIGNING_KEY")
        # print(f"PASO 8 client_toml_contents.get('SIGNING_KEY'): True")
        if not client_signing_key:
            # print(f"PASO 9 Error")
            raise ValueError(gettext("SIGNING_KEY not present on 'client_domain' TOML"))
        try:
            # print(f"PASO 10 Keypair.from_public_key(client_signing_key): True")
            Keypair.from_public_key(client_signing_key)
        except Ed25519PublicKeyInvalidError:
            # print(f"PASO 11 Error")
            raise ValueError(
                gettext("invalid SIGNING_KEY value on 'client_domain' TOML")
            )
        print(f"PASO 12 client_signing_key: {client_signing_key}")
        print(f"SERVER KEY GC3E")
        print(f"CLIENT KEY GAB5")
        return client_signing_key
