import aws_cdk as core
from exchange_rates_tracking_stack import ExchangeRatesTrackingStack


def test_exchange_rates_snapshot(expected_snapshot):
    app = core.App()
    exchange_rates_stack = ExchangeRatesTrackingStack(app, 'exchange-rates-tracking')
    template = core.Template.from_stack(exchange_rates_stack)
    assert template.to_json() == expected_snapshot
