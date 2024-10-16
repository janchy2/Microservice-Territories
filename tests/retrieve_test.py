import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lambda_function import lambda_handler
from example_requests import events


def test_retrieve_successful():
    event = events[8]
    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            {'Item': {
                'territory_name': 'Belgrade',
                'territory_type': 'locality',
                'territory_path': 'RS#426614174000#426614174001',
                'uuid': 'f236fb52ab02'
            }}
        ]
        mock_table.scan.side_effect = [
            # returns children
            {'Items': [
                {'territory_name': '11000',
                'territory_type': 'postal_code',
                'territory_path': 'RS#426614174000#426614174001#f236fb52ab02',
                'uuid': '426614174003'}
            ]}
        ]
    
        result = lambda_handler(event, None)
        body = json.loads(result['body'])
        assert body['territories'] == [
            {
                'territory_name': 'Belgrade',
                'territory_type': 'locality',
                'territory_path': 'RS#426614174000#426614174001',
                'uuid': 'f236fb52ab02'
            },
            {
                'territory_name': '11000',
                'territory_type': 'postal_code',
                'territory_path': 'RS#426614174000#426614174001#f236fb52ab02',
                'uuid': '426614174003'
            }
        ]
        assert result['statusCode'] == 200


def test_incomplete_data():
    event = events[9]
    result = lambda_handler(event, None)
    body = json.loads(result['body'])
    assert body['message'] == 'Invalid or incomplete retrieve data!'
    assert result['statusCode'] == 400


def test_non_existent_uuid():
    event = events[8]
    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            {'Item': {}}
        ]
        result = lambda_handler(event, None)
        body = json.loads(result['body'])
        assert body['message'] == 'Non-existent uuid!'
        assert result['statusCode'] == 404
