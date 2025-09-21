import json
import boto3
import os
from datetime import datetime, UTC 
from uuid import uuid4
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
table_name = os.environ['TABLE_NAME']

def handler(event, context):
    start_time = datetime.now(UTC)
    body = json.loads(event.get('body', '{}'))
    operation = body.get('operation')
    numbers = body.get('numbers', [])

    if not operation or not numbers or len(numbers) < 2:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid operation or numbers'})}
    if operation not in ['add', 'subtract', 'multiply']:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Unsupported operation'})}

    result = numbers[0]
    for num in numbers[1:]:
        if operation == 'add': result += num
        elif operation == 'subtract': result -= num
        elif operation == 'multiply': result *= num

    timestamp = datetime.now(UTC).isoformat() + 'Z'  
    item = {
        'pk': f'calc#{str(uuid4())}',
        'timestamp': timestamp,
        'type': 'calc',
        'operation': operation,
        'numbers': numbers,
        'result': result
    }

    try:
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
    except ClientError as e:
        return {'statusCode': 500, 'body': json.dumps({'error': f'DynamoDB error: {str(e)}'})}
    
    latency = (datetime.now(UTC) - start_time).total_seconds() * 1000  
    cloudwatch.put_metric_data(
        Namespace='ServerlessAPI',
        MetricData=[{
            'MetricName': 'CalcLatency',
            'Value': latency,
            'Unit': 'Milliseconds'
        }]
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'result': result, 'operation': operation, 'id': item['pk'], 'timestamp': timestamp})
    }