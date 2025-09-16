import json  
import boto3  
import os  
from datetime import datetime  
from botocore.exceptions import ClientError  

dynamodb = boto3.resource('dynamodb')  
table_name = os.environ['TABLE_NAME']  

def handler(event, context):  
    city = event.get('queryStringParameters', {}).get('city', 'London')  
    if not city:  
        return {'statusCode': 400, 'body': json.dumps({'error': 'City required'})}  

    mock_weather = {  
        'city': city,  
        'temperature': 20,  
        'humidity': 60,  
        'description': 'Partly cloudy'  
    }  
    timestamp = datetime.utcnow().isoformat() + 'Z'  
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

    return {'statusCode': 200, 'body': json.dumps(mock_weather)}  