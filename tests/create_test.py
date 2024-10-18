from unittest.mock import patch, MagicMock
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from application.app import app
from example_requests import events


client = TestClient(app)


def test_create_whole_path_successful():
    event = events[0]

    mock_uuids = [
        "123e4567-e89b-12d3-a456-426614174000",
        "223e4567-e89b-12d3-a456-426614174001",
        "323e4567-e89b-12d3-a456-426614174002",
        "423e4567-e89b-12d3-a456-426614174003",
    ]
    with patch("boto3.resource") as mock_dynamo_resource, patch(
        "uuid.uuid4", side_effect=mock_uuids
    ):
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.scan.side_effect = [
            # none of the territories exist
            {"Items": []},
            {"Items": []},
            {"Items": []},
            {"Items": []},
        ]

        response = client.post("/territories", json=event["body"])
        body = response.json()
        assert body["message"] == "Territory created successfully!"
        assert response.status_code == 201

        put_item_calls = mock_table.put_item.call_args_list
        assert len(put_item_calls) == 4

        assert put_item_calls[0][1]["Item"] == {
            "territory_name": "Belgrade",
            "territory_type": "administrative_area_1",
            "territory_path": "RS",
            "uuid": "426614174000",
        }
        assert put_item_calls[1][1]["Item"] == {
            "territory_name": "City of Belgrade",
            "territory_type": "administrative_area_2",
            "territory_path": "RS#426614174000",
            "uuid": "426614174001",
        }
        assert put_item_calls[2][1]["Item"] == {
            "territory_name": "Belgrade",
            "territory_type": "locality",
            "territory_path": "RS#426614174000#426614174001",
            "uuid": "426614174002",
        }
        assert put_item_calls[3][1]["Item"] == {
            "territory_name": "11000",
            "territory_type": "postal_code",
            "territory_path": "RS#426614174000#426614174001#426614174002",
            "uuid": "426614174003",
        }


def test_create_partial_path_successful():
    event = events[1]
    mock_uuids = [
        "123e4567-e89b-12d3-a456-426614174004",
        "223e4567-e89b-12d3-a456-426614174005",
    ]
    with patch("boto3.resource") as mock_dynamo_resource, patch(
        "uuid.uuid4", side_effect=mock_uuids
    ):
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.scan.side_effect = [
            # admin area 2 and admin area 1 exist
            {"Items": [{"uuid": "426614174001"}]},
            {"Items": [{"uuid": "426614174002"}]},
            {"Items": []},
            {"Items": []},
        ]

        response = client.post("/territories", json=event["body"])
        body = response.json()
        assert body["message"] == "Territory created successfully!"
        assert response.status_code == 201

        put_item_calls = mock_table.put_item.call_args_list
        assert len(put_item_calls) == 2

        assert put_item_calls[0][1]["Item"] == {
            "territory_name": "Malča",
            "territory_type": "locality",
            "territory_path": "RS#426614174001#426614174002",
            "uuid": "426614174004",
        }
        assert put_item_calls[1][1]["Item"] == {
            "territory_name": "18206",
            "territory_type": "postal_code",
            "territory_path": "RS#426614174001#426614174002#426614174004",
            "uuid": "426614174005",
        }


def test_postal_code_exists():
    event = events[0]
    with patch("boto3.resource") as mock_dynamo_resource:
        mock_table = MagicMock()
        mock_dynamo_resource.return_value.Table.return_value = mock_table
        mock_table.scan.side_effect = [
            # all territories exist
            {"Items": [{"uuid": "426614174001"}]},
            {"Items": [{"uuid": "426614174002"}]},
            {"Items": [{"uuid": "426614174003"}]},
            {"Items": [{"uuid": "426614174004"}]},
        ]

        response = client.post("/territories", json=event["body"])
        body = response.json()
        assert body["message"] == "Postal code already exists!"
        assert response.status_code == 409


def test_incomplete_data():
    event = events[2]
    # missing postal_code
    response = client.post("/territories", json=event["body"])
    body = response.json()
    assert body["message"] == "Invalid or incomplete territory data!"
    assert response.status_code == 400


def test_invalid_data():
    event = events[3]
    # not in Serbia
    response = client.post("/territories", json=event["body"])
    body = response.json()
    assert body["message"] == "Invalid or incomplete territory data!"
    assert response.status_code == 400
