import pytest
import boto3
from moto import mock_aws
import json
import os
os.environ['TABLE_NAME'] = 'apiData'  
from src.calc import handler

@mock_aws
def test_calc_handler():
    boto3.setup_default_session()
    dynamodb = boto3.resource('dynamodb')
    dynamodb.create_table(
        TableName='apiData',
        KeySchema=[{'AttributeName': 'pk', 'KeyType': 'HASH'}, {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'pk', 'AttributeType': 'S'}, {'AttributeName': 'timestamp', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    event = {'body': json.dumps({'operation': 'add', 'numbers': [2, 3]})}
    response = handler(event, None)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['result'] == 5
    assert body['operation'] == 'add'
    table = dynamodb.Table('apiData')
    item = table.get_item(Key={'pk': body['id'], 'timestamp': body['timestamp']})['Item']
    assert item['type'] == 'calc'