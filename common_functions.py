import boto3
import json

def connect_to_database():
    dynamodb = boto3.resource('dynamodb')
    table_name = 'territories'
    return dynamodb.Table(table_name)


def generate_response(status, message):
    return {
        'statusCode': status,
        'body': json.dumps({'message': message}),
        'headers': {'Content-Type': 'application/json'}
    }
