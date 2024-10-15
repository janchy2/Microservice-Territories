import boto3
from boto3.dynamodb.conditions import Attr
from common_functions import generate_response, connect_to_database


def delete_request(parameters):
    if 'uuid' not in parameters:
        return generate_response(400, 'Invalid or incomplete delete data!')
    table = connect_to_database()
    element = get_element(table, parameters['uuid'])
    if not element:
        return generate_response(409, 'Non-existent uuid!')
    if has_children(table, element):
        return generate_response(409, 'Territory has subterritories, it cannot be deleted!')
    delete_element(table, element)
    return generate_response(200, 'Territory deleted successfully!')


def get_element(table, uuid):
    response = table.get_item(
    Key={
        'uuid': uuid
    })
    return response.get('Item')


def has_children(table, element):
    response = table.scan(
        FilterExpression=Attr('territory_path').begins_with(element['territory_path'] + '#')
    )
    return response.get('Items', [])


def delete_element(table, element):
    table.delete_item(
        Key={
            'uuid': element['uuid']
        }
    )
