from common_functions import generate_response, connect_to_database
from boto3.dynamodb.conditions import Attr
import json


def retrieve_request(parameters):
    if 'uuid' not in parameters:
        return generate_response(400, 'Invalid or incomplete retrieve data!')
    table = connect_to_database()
    element = get_element(table, parameters['uuid'])
    if not element:
        return generate_response(404, 'Non-existent uuid!')
    return {
        'statusCode': 200,
        'body': json.dumps({'territories': retrieve(table, element)}),
        'headers': {'Content-Type': 'application/json'}
    }
    

def get_element(table, uuid):
    response = table.get_item(
    Key={
        'uuid': uuid
    })
    return response.get('Item')


def retrieve(table, element):
    # retrieves element and all its children paged if necessary
    territories = [element]
    response = table.scan(
        FilterExpression=Attr('territory_path').begins_with(element['territory_path'] + '#' + element['uuid'])
    )
    territories.extend(response['Items'])
    while 'LastEvaluatedKey' in response:
        response = table.scan(
        FilterExpression=Attr('territory_path').begins_with(element['territory_path'] + '#' + element['uuid']),
        ExclusiveStartKey=response['LastEvaluatedKey']
        )
        territories.extend(response['Items'])
    return territories
