import pytest
import boto3
from moto import mock_aws
import json
import os
os.environ['TABLE_NAME'] = 'apiData' 
from src.weather import handler

@mock_aws
def test_weather_handler():
    boto3.setup_default_session()
    dynamodb = boto3.resource('dynamodb')
    dynamodb.create_table(
        TableName='apiData',
        KeySchema=[{'AttributeName': 'pk', 'KeyType': 'HASH'}, {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'pk', 'AttributeType': 'S'}, {'AttributeName': 'timestamp', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    event = {'queryStringParameters': {'city': 'London'}}
    response = handler(event, None)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['city'] == 'London'
    assert body['temperature'] == 20
    table = dynamodb.Table('apiData')
    item = table.get_item(Key={'pk': 'weather#London', 'timestamp': body['timestamp']})['Item']
    assert item['type'] == 'weather'