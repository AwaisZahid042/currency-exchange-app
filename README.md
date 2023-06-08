#Serverless Exchange Rates Tracking Application
The Serverless Exchange Rates Tracking Application is a serverless application developed in the AWS Lambda environment, deployable using AWS CDK. It collects exchange rates data from the European Central Bank (ECB) and provides a REST API for fetching the latest exchange rates. The application utilizes a DynamoDB table for storing the exchange rates and includes a scheduled Lambda function for periodically updating the exchange rates.

Components
DynamoDB table: Stores the exchange rates data.
Lambda function (UpdateExchangeRates): Runs at 16:00:00 UTC daily to update the exchange rates in DynamoDB.
REST API: Provides endpoints for fetching exchange rates.
Lambda function (GetExchangeRates): Connected to the REST API, reads exchange rates from DynamoDB.
#Architecture
The application follows the following architecture:

#Architecture Diagram

#REST API
Once deployed, the application exposes a REST API endpoint that provides the latest exchange rates published by the ECB, along with the change in rates compared to the last published update.

Sample Response:

json
Copy code
{
  "update_date": "2022-12-10",
  "publish_date": "2022-12-09",
  "base_currency": "EUR",
  "exchange_rates": [
    {
      "currency": "AUD",
      "rate": "1.5553",
      "change": "-0.0037",
      "change_percentage": "-0.2373 %"
    },
    {
      "currency": "BGN",
      "rate": "1.9558",
      "change": "0.0",
      "change_percentage": "0.0 %"
    },
    {
      "currency": "BRL",
      "rate": "5.5457",
      "change": "+0.0577",
      "change_percentage": "+1.0514 %"
    },
    ...
  ]
}
Deployment
Required Tools
AWS CLI (Tested Version: 2.9.5)
AWS CDK (Tested Version: 2.54.0)
NodeJS (Tested Version: 18.12.1)
npm (Tested Version: 8.19.2)
Python3 (Tested Version: 3.8.15)
pip (Tested Version: 22.3)
Localstack (Tested Version: 1.3.0)
Instructions
Note: These instructions have been verified on Linux (Ubuntu 22.04).

Install AWS CLI.
Install AWS CDK:
shell
Copy code
$ npm install -g aws-cdk
Clone the repository and change the working directory to the repository root folder.
Create and activate a Python virtual environment:
shell
Copy code
# Create virtual environment
$ python3 -m venv .venv
# Activate virtual environment
$ source .venv/bin/activate
Install the required Python packages:
shell
Copy code
$ pip install -r requirements.txt
From here, you can choose to deploy the application either on AWS or locally using Localstack.
Deploy on AWS
Configure AWS CLI:
Note: AWS CLI should be configured with user credentials having privileges to create resources on AWS that are required for the application.

Bootstrap CDK to set up necessary resources in AWS for CDK deployments:
shell
Copy code
$ cdk bootstrap
(Optional) Synthesize code to generate a CloudFormation template:
shell
Copy code
$ cdk synth
Deploy the application on AWS:
shell
Copy code
$ cdk deploy
On successful deployment, a link to a public REST endpoint is printed on the console. Append the resource name "exchangerates" to the link for the exchange rates API. You can open the API URL in a browser or use a utility like curl to fetch exchange rates data.

Sample REST endpoint:

markdown
Copy code
https://**********.execute-api.us-east-1.amazonaws.com/prod/
Exchange rates API:

markdown
Copy code
https://**********.execute-api.us-east-1.amazonaws.com/prod/exchangerates
(Optional) Delete the application, removing allocated resources:
shell
Copy code
$ cdk destroy
Deploy locally on Localstack
Install and start Localstack.
Install the cdklocal tool:
shell
Copy code
$ npm install -g aws-cdk-local
Install the awslocal tool:
shell
Copy code
$ pip install awscli-local
Bootstrap Localstack for CDK deployment:
shell
Copy code
$ cdklocal bootstrap
(Optional) Synthesize code to generate a CloudFormation template:
shell
Copy code
$ cdklocal synth
Deploy the application on Localstack:
shell
Copy code
$ cdklocal deploy
After deployment, the TriggerFunction from CDK executes a Lambda function to populate the initial exchange rates data. However, Localstack does not support TriggerFunction, so the Lambda function has to be manually invoked once.

shell
Copy code
# Get a list of deployed Lambda functions
$ awslocal lambda list-functions

# From the response, find the Lambda function with 'updateexchangerates' in its function name
# Manually invoke the Lambda function to populate initial data in the database
$ awslocal lambda invoke --function-name <function name> /dev/null
A link to a local REST endpoint is printed on the console after deployment. Append the resource name "exchangerates" to the link for the exchange rates API. You can open the API URL in a browser or use a utility like curl to fetch exchange rates data.

Sample REST endpoint:

markdown
Copy code
https://**********.execute-api.localhost.localstack.cloud:4566/prod/
Exchange rates API:

markdown
Copy code
https://**********.execute-api.localhost.localstack.cloud:4566/prod/exchangerates
Run Tests
Install the dependencies:
shell
Copy code
$ pip install -r requirements-dev.txt
Execute the tests:
shell
Copy code
$ python3 -m pytest -v