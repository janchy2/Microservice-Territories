from create_functions import create_request
from update_functions import update_request

def lambda_handler(event, context):
    method = event['httpMethod']
    if method == 'POST':
        return create_request(event['body'])
    elif method == 'PATCH':
        return update_request(event['body'])
    