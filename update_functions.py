from common_functions import generate_response, connect_to_database


def update_request(body):
    # body should contain uuid of postal code that should be updated and uuid of new territory - locality or admin area 2
    if len(body) != 2 or 'postal_code_uuid' not in body or 'new_territory_uuid' not in body:
        return generate_response(400, 'Invalid or incomplete update data!')
    table = connect_to_database()
    postal_code_elem = get_element(table, body['postal_code_uuid'])
    if not postal_code_elem or postal_code_elem['territory_type'] != 'postal_code':
        return generate_response(400, 'Non-existent or invalid postal code uuid!')
    new_territory_elem = get_element(table, body['new_territory_uuid'])
    if not new_territory_elem or (new_territory_elem['territory_type'] != 'locality' and new_territory_elem['territory_type'] != 'administrative_area_2'):
        return generate_response(400, 'Non-existent or invalid new territory uuid!')
    
    if new_territory_elem['territory_type'] == 'locality':
        change_locality_path(table, postal_code_elem, new_territory_elem)
    else:
        change_admin_area_2(table, postal_code_elem, new_territory_elem)
    return generate_response(200, 'Territory updated successfully!')

    
def get_element(table, uuid):
    response = table.get_item(
    Key={
        'uuid': uuid
    })
    return response.get('Item')


def change_locality_path(table, postal_code_elem, locality_elem):
    new_path = locality_elem['territory_path'] + '#' + locality_elem['uuid']
    table.update_item(
        Key={
            'uuid': postal_code_elem['uuid']
        },
        UpdateExpression="set territory_path = :new_path",
        ExpressionAttributeValues={
            ':new_path': new_path
        }
    )


def change_admin_area_2(table, postal_code_elem, admin_area_elem):
    locality_elem = change_admin_area_path_for_locality(table, postal_code_elem, admin_area_elem)
    change_locality_path(table, postal_code_elem, locality_elem)


def change_admin_area_path_for_locality(table, postal_code_elem, admin_area_elem):
    locality_uuid = postal_code_elem['territory_path'].split('#')[-1]
    new_path = admin_area_elem['territory_path'] + '#' + admin_area_elem['uuid']
    response = table.update_item(
        Key={
            'uuid': locality_uuid
        },
        UpdateExpression="set territory_path = :new_path",
        ExpressionAttributeValues={
            ':new_path': new_path
        },
        ReturnValues="ALL_NEW"
    )
    # return updated locality
    return response['Attributes']
