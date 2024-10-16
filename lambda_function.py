from create_functions import create_request
from update_functions import update_request
from delete_functions import delete_request
from retrieve_functions import retrieve_request
from common_functions import generate_response

def lambda_handler(event, context):
    method = event['httpMethod']
    try:
        if method == 'POST':
            return create_request(event['body'])
        elif method == 'PATCH':
            return update_request(event['body'])
        elif method == 'DELETE':
            return delete_request(event['pathParameters'])
        elif method == 'GET':
            return retrieve_request(event['pathParameters'])
        else:
            return generate_response(400, 'Method not supported!')
    except KeyError:
        return generate_response(400, 'Invalid request, missing body or path parameters!')
    