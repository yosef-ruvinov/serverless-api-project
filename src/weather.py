import json
import boto3
import os
from datetime import datetime, UTC  
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
table_name = os.environ['TABLE_NAME']

def handler(event, context):
    start_time = datetime.now(UTC)
    city = event.get('queryStringParameters', {}).get('city', 'London')
    if not city:
        return {'statusCode': 400, 'body': json.dumps({'error': 'City required'})}

    mock_weather = {
        'city': city,
        'temperature': 20,
        'humidity': 60,
        'description': 'Partly cloudy'
    }
    timestamp = datetime.now(UTC).isoformat() + 'Z'  
    item = {
        'pk': f'weather#{city}',
        'timestamp': timestamp,
        'type': 'weather',
        'data': mock_weather
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
            'MetricName': 'WeatherLatency',
            'Value': latency,
            'Unit': 'Milliseconds'
        }]
    )

    return {
        'statusCode': 200,
        'body': json.dumps({**mock_weather, 'timestamp': timestamp})  
    }