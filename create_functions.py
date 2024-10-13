import json
import uuid
import boto3


def create_request(body):
    territory_data = extract_data(body)
    if not territory_data:
        return generate_response(400, 'Invalid or incomplete territory data!')
    table = connect_to_database()
    levels = ['administrative_area_1', 'administrative_area_2', 'locality', 'postal_code']
    path = 'RS' # root is RS - we need it because of the secondary index
    for level in levels:
        element_id = check_if_element_exists(table, territory_data[level], level)
        if element_id and level == 'postal_code':
            # element already exists, conflict
            return generate_response(409, 'Postal code already exists!')
        if not element_id:
            element_id = create_element(table, territory_data[level], level, path)
        path += '#' + element_id
    return generate_response(201, 'Territory created successfully!')


def extract_data(body):
    if 'results' in body and len(body['results']):
        result = body['results'][0]
        address_components = result.get('address_components', [])
        territory_data = {}
        for component in address_components:
                if 'locality' in component['types']:
                    territory_data['locality'] = component['long_name']
                elif 'administrative_area_level_2' in component['types']:
                    territory_data['administrative_area_2'] = component['long_name']
                elif 'administrative_area_level_1' in component['types']:
                    territory_data['administrative_area_1'] = component['long_name']
                elif 'postal_code' in component['types']:
                    territory_data['postal_code'] = component['long_name']
                elif 'country' in component['types']:
                    territory_data['country'] = component['long_name']
        if len(territory_data) == 5 and territory_data['country'] == 'Serbia':
            # all attributes present and territory belongs to Serbia
           return territory_data

        
def connect_to_database():
    dynamodb = boto3.resource('dynamodb')
    table_name = 'territories'
    return dynamodb.Table(table_name)


def check_if_element_exists(table, name, type):
    response = table.scan(
            FilterExpression='territory_name = :name_value AND territory_type = :type_value',
            ExpressionAttributeValues={
                ':name_value': name,
                ':type_value': type
            }
        )
    if response['Items']:
        # element exists
        return response['Items'][0]['uuid']


def create_element(table, name, type, path):
    uuid = generate_uuid()
    item_data = {
        'uuid': uuid,
        'territory_name': name,
        'territory_type': type,
        'path': path
    }
    table.put_item(Item=item_data)
    return uuid


def generate_uuid():
    # create UUID v4 and extract the last part
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    return uuid_str.split('-')[-1]


def generate_response(status, message):
    return {
        'statusCode': status,
        'body': json.dumps({'message': message}),
        'headers': {'Content-Type': 'application/json'}
    }
