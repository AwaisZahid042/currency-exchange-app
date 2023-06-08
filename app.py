#!/usr/bin/env python3

import aws_cdk as cdk

from exchange_rates_tracking.exchange_rates_tracking_stack import ExchangeRatesTrackingStack

APP = cdk.App()
ExchangeRatesTrackingStack(APP, 'exchange-rates-tracking')

APP.synth()
