import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid

def lambda_handler(event, context):
    print(" Starting Create Device Lambda Function")
    
    table_name = os.environ['DEVICES_TABLE_NAME']
    device_table = boto3.resource('dynamodb').Table(table_name)
    
    eventBody = json.loads(event['body'])
    uid = uuid().hex
    nowtime = datetime.now().strftime('%x-%X')
    print("UID is "+uid)
    
    #default error response
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameters: Missing device parameters. deviceName and deviceType required.\"}"
    }
    
    if 'device' in eventBody:
      inDevice = eventBody['device']
      if 'deviceName' in inDevice and 'deviceType' in inDevice:
        roomID = None
        if event['pathParameters'] and 'roomID' in event['pathParameters']:
          roomID = event['pathParameters']['roomID']
        device = {
            'uuid': uid,
            'roomID': roomID,
            'deviceName': inDevice['deviceName'],
            'deviceType': inDevice['deviceType'],
            'created_at': nowtime,
            'updated_at': nowtime
        }
        device_table.put_item(Item=device)
        device['path'] = "/devices/"+uid
        response = {
            "isBase64Encoded": "false",
            "statusCode": 200,
            "body": "{\"device\": "+json.dumps(device)+" }"
        }
    
    return response
