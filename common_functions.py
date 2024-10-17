import boto3
from fastapi.responses import JSONResponse

def connect_to_database():
    dynamodb = boto3.resource('dynamodb')
    table_name = 'territories'
    return dynamodb.Table(table_name)


def generate_response(status, message):
    return JSONResponse(status_code=status, content={'message': message})
