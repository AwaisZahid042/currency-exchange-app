import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = os.environ.get('TABLE_NAME')

if 'LOCALSTACK_HOSTNAME' in os.environ:
    endpoint_url = f'http://{os.environ.get("LOCALSTACK_HOSTNAME")}:4566'
else:
    endpoint_url = None


def handler(event, context):
    '''
    Fetch exchange rates of tracked currencies from the database.
    '''
    logger.info('Fetching exchange rates from the database')
    items = read_from_db()

    if not items:
        logger.info('No data available')
        error_message = "No exchange rate data available at the moment. Please try again later."
        return {'statusCode': 200, 'body': json.dumps({'error': error_message}, indent=4)}

    logger.info('Constructing response')
    response = {
        'update_date': 'N/A',
        'publish_date': 'N/A',
        'base_currency': 'EUR',
        'exchange_rates': []
    }

    for item in items:
        if item['id'] in ('update_date', 'publish_date'):
            response[item['id']] = item['value']
        else:
            currency_data = {
                'currency': item['id'],
                'rate': item['value'],
                'change': item['diff'],
                'change_percentage': item['diff_percent']
            }
            response['exchange_rates'].append(currency_data)

    response['exchange_rates'] = sorted(response['exchange_rates'], key=lambda x: x['currency'])

    return {'statusCode': 200, 'body': json.dumps(response, indent=4)}


def read_from_db():
    '''
    Read exchange rate records from the database.
    '''
    dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url)
    table = dynamodb.Table(table_name)

    exchange_rates = []

    response = table.scan()
    exchange_rates.extend(response['Items'])

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        exchange_rates.extend(response['Items'])

    return exchange_rates
