import boto3
import os
from fastapi.responses import JSONResponse
from typing import Any, Optional


def connect_to_database() -> Any:
    dynamodb_endpoint: Optional[str] = os.getenv("DYNAMODB_ENDPOINT")
    dynamodb = boto3.resource(
        "dynamodb", region_name="eu-south-1", endpoint_url=dynamodb_endpoint
    )
    return create_table_if_not_exists(dynamodb)


def create_table_if_not_exists(dynamodb: Any) -> Any:
    table_name: str = "territories"
    try:
        table = dynamodb.Table(table_name)
        table.load()
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "uuid", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "uuid", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
    return table


def generate_response(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"message": message})
