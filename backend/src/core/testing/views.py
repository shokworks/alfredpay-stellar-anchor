import os

import toml
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from polaris.sep1.views import PolarisPlainTextRenderer, generate_toml
from polaris.integrations import registered_toml_func
from polaris.models import Asset

from config.settings import base as settings


@api_view(["GET"])
@renderer_classes([PolarisPlainTextRenderer])
def generate_toml(generate_toml):
    toml_dict1 = {
        "VERSION": "0.1.1",
    }
    toml_dict2 = {
        "NETWORK_PASSPHRASE": settings.POLARIS_STELLAR_NETWORK_PASSPHRASE,
        "WEB_AUTH_ENDPOINT": os.path.join(settings.POLARIS_HOST_URL, "auth"),
        # "SIGNING_KEY": settings.SIGNING_KEY,
        "TRANSFER_SERVER": os.path.join(settings.POLARIS_HOST_URL, "sep24"),
        "TRANSFER_SERVER_SEP0024": os.path.join(settings.POLARIS_HOST_URL, "sep24"),
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
