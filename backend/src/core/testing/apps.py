from django.apps import AppConfig


class TestingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.testing'

"""
def ready(self):
    from polaris.integrations import register_integrations
    from integrations import (
        MyRailsIntegration,
        # MyDepositIntegration,
        # MyWithdrawalIntegration,
        # MyCustomerIntegration,
        # toml_integration,
        # fee_integrations,
        # scripts_integration,
        # info_integration
    )

    register_integrations(
        deposit=MyDepositIntegration(),
        withdrawal=MyWithdrawalIntegration(),
        customer=MyCustomerIntegration(),
        toml=toml_integration,
        sep6_info=info_integration,
        fee=fee_integration
    )
"""
