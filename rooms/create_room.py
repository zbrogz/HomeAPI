import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid

def lambda_handler(event, context):
    print(" Starting Create Room Lambda Function")
    
    table_name = os.environ['ROOMS_TABLE_NAME']
    room_table = boto3.resource('dynamodb').Table(table_name)
    
    eventBody = json.loads(event['body'])
    uid = uuid().hex
    nowtime = datetime.now().strftime('%x-%X')
    print("UID is "+uid)
    
    if not 'name' in eventBody:
        response = {
            "isBase64Encoded": "false",
            "statusCode": 400,
            "body": "{\"message\": \"Invalid paramters.\"}"
        }
        #raise Exception("Missing or invalid paramters.")
        return json.dumps(response)

    room = {
        'uuid': uid,
        'name': eventBody['name'],
        'created_at': nowtime,
        'updated_at': nowtime
    }

    room_table.put_item(Item=room)

    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": json.dumps(room)
    }

    
    return response