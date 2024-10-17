from unittest.mock import patch, MagicMock
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app


client = TestClient(app)


def test_retrieve_successful():
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
    
        response = client.get("/territories/f236fb52ab02")
        body = response.json()
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
        assert response.status_code == 200


def test_non_existent_uuid():
    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            {'Item': {}}
        ]
        response = client.get("/territories/f236fb52ab02")
        body = response.json()
        assert body['message'] == 'Non-existent uuid!'
        assert response.status_code == 404
