from unittest.mock import patch, MagicMock
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app


client = TestClient(app)


def test_delete_successful():
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
    
        response = client.delete("/territories/f236fb52ab08")
        body = response.json()
        assert body['message'] == 'Territory deleted successfully!'
        assert response.status_code == 200



def test_has_subterritories():
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
    
        response = client.delete("/territories/f236fb52ab08")
        body = response.json()
        assert body['message'] == 'Territory has subterritories, it cannot be deleted!'
        assert response.status_code == 409


def test_non_existent_uuid():
    with patch('boto3.resource') as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = [
            {'Item': {}}
        ]
        response = client.delete("/territories/f236fb52ab08")
        body = response.json()
        assert body['message'] == 'Non-existent uuid!'
        assert response.status_code == 404
