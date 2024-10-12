import json
from create_functions import create_request

def lambda_handler(event, context):
    method = event['httpMethod']
    if method == 'POST':
        return create_request(event['body'])
    