import boto3
import os
from fastapi.responses import JSONResponse


def connect_to_database():
    dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8001")
    dynamodb = boto3.resource("dynamodb", endpoint_url=dynamodb_endpoint)
    table_name = "territories"
    return dynamodb.Table(table_name)


def generate_response(status, message):
    return JSONResponse(status_code=status, content={"message": message})
