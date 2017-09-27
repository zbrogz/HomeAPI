import os
import boto3
import json
from datetime import datetime
#from uuid import uuid4 as uuid

def get_all_rooms():
    print("Getting Rooms")
    
    table_name = os.environ['ROOMS_TABLE_NAME']
    rooms_table = boto3.resource('dynamodb').Table(table_name)
    
    
    result = rooms_table.scan()
    rooms = result['Items']
    while 'LastEvaluateKey' in result:
            result = rooms_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
            rooms += result['Items']
            
    return rooms

def lambda_handler(event, context):
    print(" Starting Get Room Lambda Function")
    
    rooms = get_all_rooms()
    
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": json.dumps(rooms)
    }
    
    return response