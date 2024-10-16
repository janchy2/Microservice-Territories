import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lambda_function import lambda_handler
from example_requests import events


def test_delete_successful():
    event = events[6]
    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            # returns postal code element that should be deleted
            {'Item': {
                'territory_name': '18206',
                'territory_type': 'postal_code',
                'territory_path': 'RS#426614174001#426614174002#426614174004',
                'uuid': 'f236fb52ab08'
            }}
        ]
        mock_table.scan.side_effect = [
            # no children
            {'Items': []}
        ]
    
        result = lambda_handler(event, None)
        body = json.loads(result['body'])
        assert body['message'] == 'Territory deleted successfully!'
        assert result['statusCode'] == 200



def test_has_subterritories():
    event = events[6]
    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            # returns postal code element that should be deleted
            {'Item': {
                'territory_name': '18206',
                'territory_type': 'postal_code',
                'territory_path': 'RS#426614174001#426614174002#426614174004',
                'uuid': 'f236fb52ab08'
            }}
        ]
        mock_table.scan.side_effect = [
            # has children
            {'Items': {
                'territory_name': '11000',
                'territory_type': 'postal_code',
                'territory_path': 'RS#426614174000#426614174001#426614174002',
                'uuid': '426614174003'
            }}
        ]
    
        result = lambda_handler(event, None)
        body = json.loads(result['body'])
        assert body['message'] == 'Territory has subterritories, it cannot be deleted!'
        assert result['statusCode'] == 409



def test_invalid_path_parameter():
    event = events[7]
    result = lambda_handler(event, None)
    body = json.loads(result['body'])
    assert body['message'] == 'Invalid or incomplete delete data!'
    assert result['statusCode'] == 400


def test_non_existent_uuid():
    event = events[6]
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
