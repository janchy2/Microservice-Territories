import json
from unittest.mock import patch
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lambda_function import lambda_handler

def test_create_region_successful():
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            "results": [
                {
                    "address_components": [
                        {
                            "long_name": "Trg Republike",
                            "short_name": "Trg Republike",
                            "types": ["premise"]
                        },
                        {
                            "long_name": "Belgrade",
                            "short_name": "Belgrade",
                            "types": ["locality", "political"]
                        },
                        {
                            "long_name": "City of Belgrade",
                            "short_name": "City of Belgrade",
                            "types": ["administrative_area_level_2", "political"]
                        },
                        {
                            "long_name": "Belgrade",
                            "short_name": "Belgrade",
                            "types": ["administrative_area_level_1", "political"]
                        },
                        {
                            "long_name": "Serbia",
                            "short_name": "RS",
                            "types": ["country", "political"]
                        },
                        {
                            "long_name": "11000",
                            "short_name": "11000",
                            "types": ["postal_code"]
                        }
                    ],
                    "formatted_address": "Trg Republike, 11000 Belgrade, Serbia",
                    "geometry": {
                        "location": {
                            "lat": 44.8181,
                            "lng": 20.4633
                        },
                        "location_type": "ROOFTOP",
                        "viewport": {
                            "northeast": {
                                "lat": 44.81944998029149,
                                "lng": 20.4646499802915
                            },
                            "southwest": {
                                "lat": 44.81675201970849,
                                "lng": 20.4619520197085
                            }
                        }
                    },
                    "place_id": "ChIJn4ml_XQx1kARjD5fKaNh0Bk",
                    "types": ["street_address"]
                }
            ],
            "status": "OK"
        })
    }
    
    result = lambda_handler(event, None)
    
    assert result['statusCode'] == 201
    body = json.loads(result['body'])
    assert body['message'] == 'Territory created successfully!'
