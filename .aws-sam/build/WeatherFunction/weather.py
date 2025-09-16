import json  
import boto3  
import os  
from datetime import datetime  
from uuid import uuid4  # For unique IDs if needed  

dynamodb = boto3.resource('dynamodb')  
table_name = os.environ['TABLE_NAME']  

def handler(event, context):  
    # Get city from query params (from API Gateway event)  
    city = event.get('queryStringParameters', {}).get('city', 'London')  # Default to London  

    # Generate mock weather data  
    mock_weather = {  
        'city': city,  
        'temperature': 20,  # Fixed mock; or random: import random; random.randint(10, 30)  
        'humidity': 60,  
        'description': 'Partly cloudy'  
    }  

    # Real-time timestamp  
    timestamp = datetime.utcnow().isoformat() + 'Z'  

    # Prepare DynamoDB item  
    item = {  
        'pk': f'weather#{city}',  
        'timestamp': timestamp,  
        'type': 'weather',  
        'data': mock_weather  
    }  

    # Put item in DynamoDB  
    table = dynamodb.Table(table_name)  
    table.put_item(Item=item)  

    # Return response  
    return {  
        'statusCode': 200,  
        'body': json.dumps(mock_weather)  
    }  