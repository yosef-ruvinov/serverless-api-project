import json  
import boto3  
import os  
from datetime import datetime  
from uuid import uuid4  

dynamodb = boto3.resource('dynamodb')  
table_name = os.environ['TABLE_NAME']  

def handler(event, context):  
    # Parse body from POST (API Gateway event)  
    body = json.loads(event.get('body', '{}'))  
    operation = body.get('operation')  
    numbers = body.get('numbers', [])  

    # Validate inputs  
    if not operation or not numbers or len(numbers) < 2:  
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid operation or numbers'})}  
    if operation not in ['add', 'subtract', 'multiply']:  
        return {'statusCode': 400, 'body': json.dumps({'error': 'Unsupported operation'})}  

    # Compute result  
    result = numbers[0]  
    for num in numbers[1:]:  
        if operation == 'add': result += num  
        elif operation == 'subtract': result -= num  
        elif operation == 'multiply': result *= num  

    # Store in DynamoDB  
    timestamp = datetime.utcnow().isoformat() + 'Z'  
    item = {  
        'pk': f'calc#{str(uuid4())}',  
        'timestamp': timestamp,  
        'type': 'calc',  
        'operation': operation,  
        'numbers': numbers,  
        'result': result  
    }  
    table = dynamodb.Table(table_name)  
    table.put_item(Item=item)  

    # Return response  
    return {  
        'statusCode': 200,  
        'body': json.dumps({'result': result, 'operation': operation, 'id': item['pk'], 'timestamp': timestamp})  
    }  
