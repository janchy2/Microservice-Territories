import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lambda_function import lambda_handler


def test_update_locality_successful():
    event = {
        "httpMethod" : "PATCH",
        "body" : {
            "postal_code_uuid": "f236fb52ab06",
            "new_territory_uuid": "65f51efbf5e7"
        }
    }

    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            # returns postal code and locality elements
            {'Item': {
                'territory_name': '18206',
                'territory_type': 'postal_code',
                'territory_path': 'RS#426614174001#426614174002#426614174004',
                'uuid': 'f236fb52ab06'
            }},
            {'Item': {
                'territory_name': 'Belgrade',
                'territory_type': 'locality',
                'territory_path': 'RS#426614174000#426614174001',
                'uuid': '65f51efbf5e7'
            }}
        ]
    
        result = lambda_handler(event, None)
        body = json.loads(result['body'])
        assert body['message'] == 'Territory updated successfully!'
        assert result['statusCode'] == 204

        update_item_calls = mock_table.update_item.call_args_list
        assert update_item_calls[0][1]['Key'] == {'uuid': 'f236fb52ab06'}
        assert update_item_calls[0][1]['UpdateExpression'] == "set territory_path = :new_path"
        assert update_item_calls[0][1]['ExpressionAttributeValues'] == {':new_path': 'RS#426614174000#426614174001#65f51efbf5e7'}


def test_update_admin_area_2_successful():
    event = {
        "httpMethod" : "PATCH",
        "body" : {
            "postal_code_uuid": "f236fb52ab06",
            "new_territory_uuid": "65f51efbf5e7"
        }
    }

    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            # returns postal code and admin area 2 elements
            {'Item': {
                'territory_name': '18206',
                'territory_type': 'postal_code',
                'territory_path': 'RS#426614174001#426614174002#426614174004',
                'uuid': 'f236fb52ab06'
            }},
            {'Item': {
                'territory_name': 'City of Belgrade',
                'territory_type': 'administrative_area_2',
                'territory_path': 'RS#426614174000',
                'uuid': '65f51efbf5e7'
            }}
        ]

        mock_table.update_item.side_effect = [
            {'Attributes': {
                'uuid': '426614174004',
                'territory_path': 'RS#426614174000#65f51efbf5e7'
            }},
            None
        ]
    
        result = lambda_handler(event, None)
        body = json.loads(result['body'])
        assert body['message'] == 'Territory updated successfully!'
        assert result['statusCode'] == 204

        update_item_calls = mock_table.update_item.call_args_list
        assert update_item_calls[0][1]['Key'] == {'uuid': '426614174004'}
        assert update_item_calls[0][1]['UpdateExpression'] == "set territory_path = :new_path"
        assert update_item_calls[0][1]['ExpressionAttributeValues'] == {':new_path': 'RS#426614174000#65f51efbf5e7'}

        assert update_item_calls[1][1]['Key'] == {'uuid': 'f236fb52ab06'}
        assert update_item_calls[1][1]['UpdateExpression'] == "set territory_path = :new_path"
        assert update_item_calls[1][1]['ExpressionAttributeValues'] == {':new_path': 'RS#426614174000#65f51efbf5e7#426614174004'}
