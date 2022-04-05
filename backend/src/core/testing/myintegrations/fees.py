"""
from typing import Dict, List
from decimal import Decimal

from rest_framework.request import Request

from core.polaris import settings
from core.polaris.models import Asset
from core.polaris.utils import getLogger

logger = getLogger(polaris)

def calculate_fee(
    fee_params: Dict, *_args: List, request: Request = None, **_kwargs: Dict
) -> Decimal:
    amount = fee_params["amount"]
    asset = Asset.objects.filter(code=fee_params["asset_code"]).first()
    # asset = Asset.objects.all().first()
    print(f"asset: {asset}")
    if fee_params["operation"] == settings.OPERATION_WITHDRAWAL:
        fee_percent = asset.withdrawal_fee_percent
        fee_fixed = asset.withdrawal_fee_fixed
    elif fee_params["operation"] == settings.OPERATION_DEPOSIT:
        fee_percent = asset.deposit_fee_percent
        fee_fixed = asset.deposit_fee_fixed
    elif fee_params["operation"] == "send":
        fee_percent = asset.send_fee_percent
        fee_fixed = asset.send_fee_fixed
    # elif Asset.objects.filter(code="PODC").first():
    #     print(f"asset: {asset}")
    #     amount = srt(float(fee_params["amount"])*57)
    else:
        raise ValueError("invalid 'operation'")

    return round(
        fee_fixed + (fee_percent / Decimal("100") * Decimal(amount)),
        asset.significant_decimals,
    )


registered_fee_func = calculate_fee
"""
