import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    print(" Starting Update Room Lambda Function")
    
    table_name = os.environ['ROOMS_TABLE_NAME']
    room_table = boto3.resource('dynamodb').Table(table_name)
    
    eventBody = json.loads(event['body'])

    nowtime = datetime.now().strftime('%x-%X')
    
    if 'roomName' in eventBody and event['pathParameters'] and 'roomID' in event['pathParameters']:
        uuid = event['pathParameters']['roomID']

        result = room_table.update_item(
              Key={'uuid': uuid},
              UpdateExpression="set roomName = :n",
              ExpressionAttributeValues={':n': eventBody['roomName']})
        response = {
            "isBase64Encoded": "false",
            "statusCode": 200,
            "body": "{\"message\": \"Room updated\"}"
        }
    else:
        response = {
            "isBase64Encoded": "false",
            "statusCode": 400,
            "body": "{\"errorMessage\": \"Invalid Parameters: Missing roomName\"}"
        }

    
    return response
