from django.apps import AppConfig


class TestingConfig(AppConfig):
    name = "core.testing"
    default_auto_field = "django.db.models.BigAutoField"


def ready(self):
    from core.polaris.integrations import register_integrations
    from myintegrations import (
        MyRailsIntegration,
        MyDepositIntegration,
        MyWithdrawalIntegration,
        # MyCustomerIntegration,
        # toml_integration,
        # registered_fee_func,
        # scripts_integration,
        info_integration
    )

    register_integrations(
        deposit=MyDepositIntegration(),
        withdrawal=MyWithdrawalIntegration(),
        # customer=MyCustomerIntegration(),
        # toml=toml_integration,
        sep6_info=info_integration,
        # fee=registered_fee_func
    )
