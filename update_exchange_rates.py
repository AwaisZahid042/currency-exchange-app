import os
import sys
import logging
import urllib.error
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

import boto3

# Exchange rates XML file download link
DOWNLOAD_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml'

# logger
logger = logging.getlogger()
logger.setLevel(logging.INFO)

# Dynamodb table name
TABLE_NAME = os.environ['TABLE_NAME']

# Endpoint URL, required for execution on localstack
ENDPOINT_URL = f'http://{os.environ.get("LOCALSTACK_HOSTNAME", "")}:4566'


def handler(event, context):
    '''
    Update exchange rates in database.
    '''
    logger.info('Getting exchange rates data from European Central Bank')
    date, exchange_rates = get_exchange_rates()
    logger.info('Updating exchange rates in database')
    update_exchange_rates(date, exchange_rates)
    logger.info('Job completed')


def update_exchange_rates(date, exchange_rates):
    '''
    Update exchange rates in database.
    '''
    dynamodb = boto3.client('dynamodb', endpoint_url=ENDPOINT_URL)
    items = []
    # Exchange rates
    for currency, data in exchange_rates.items():
        data['id'] = currency
        items.append({'PutRequest': {'Item': data}})
    # Dates
    items.extend([
        {'PutRequest': {'Item': {'id': 'publish_date', 'value': date}}},
        {'PutRequest': {'Item': {'id': 'update_date', 'value': datetime.utcnow().strftime('%Y-%m-%d')}}}
    ])
    # Batch write to database
    dynamodb.batch_write_item(
        RequestItems={
            TABLE_NAME: items
        }
    )


def get_exchange_rates():
    '''
    Get exchange rate data (current and difference) from European Central Bank.
    '''
    # Download XML file having exchange rates data
    try:
        response = urllib.request.urlopen(DOWNLOAD_URL, timeout=30)
    except urllib.error.URLError as err:
        logger.critical('Failed to download exchange rates data from %s', DOWNLOAD_URL)
        logger.critical(err)
        sys.exit(1)

    # Parse XML and read exchange rates of last 2 days
    context = iter(ET.iterparse(response, events=('start', 'end')))
    _, root = next(context)  # Get root element
    data = []
    for event, elem in context:
        if event == 'end' and elem.tag == '{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube':
            daily_data = {
                'date': elem[0].attrib['time'].strip(),
                'rates': {rate.attrib['currency'].strip(): float(rate.attrib['rate'].strip()) for rate in elem}
            }
            data.append(daily_data)
            if len(data) == 2:
                break
            root.clear()  # Clear element to free memory

    # Log error and exit if data parsing fails
    if len(data) < 2:
        logger.critical('Failed to read exchange rates from XML: %s', DOWNLOAD_URL)
        sys.exit(1)

    # Latest rates
    date = data[0]['date']
    latest_rates = data[0]['rates']
    # Previous day rates
    previous_rates = data[1]['rates']
    # Exchange rates document with current rates and difference
    exchange_rates = {}
    for currency, rate in latest_rates.items():
        if currency not in previous_rates:
            continue
        # Previous rate
        p_rate = previous_rates[currency]
        # Difference
        diff = round(rate - p_rate, 4) or 0.0
        # Difference in percentage
        diff_percent = round((diff / p_rate) * 100, 4) or 0.0
        exchange_rates[currency] = {'value': rate, 'diff': diff, 'diff_percent': diff_percent}

    return date, exchange_rates
