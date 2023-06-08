import aws_cdk as core
import aws_cdk.assertions as assertions
from exchange_rates_tracking_stack import ExchangeRatesTrackingStack


def setup_stack():
    app = core.App()
    stack = ExchangeRatesTrackingStack(app, 'exchange-rates-tracking')
    template = assertions.Template.from_stack(stack)
    return template


def test_dynamodb_table_created():
    template = setup_stack()
    template.has_resource_properties('AWS::DynamoDB::Table', {
        'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}]
    })
    template.has_resource('AWS::DynamoDB::Table', {'DeletionPolicy': 'Delete'})


def test_update_lambda_created():
    template = setup_stack()
    template.has_resource_properties('AWS::Lambda::Function', {
        'Handler': 'update_exchange_rates.handler',
        'Runtime': 'python3.8',
        'Timeout': 300,
        'Environment': {'Variables': {'TABLE_NAME': {}}}
    })


def test_read_lambda_created():
    template = setup_stack()
    template.has_resource_properties('AWS::Lambda::Function', {
        'Handler': 'get_exchange_rates.handler',
        'Runtime': 'python3.8',
        'Timeout': 30,
        'Environment': {'Variables': {'TABLE_NAME': {}}}
    })


def test_rest_api_created():
    template = setup_stack()
    template.has_resource_properties('AWS::ApiGateway::RestApi', {
        'Name': 'api-exchange-rates'
    })
    template.has_resource_properties('AWS::ApiGateway::Resource', {
        'PathPart': 'exchangerates'
    })
    template.has_resource_properties('AWS::ApiGateway::Method', {
        'HttpMethod': 'GET'
    })
