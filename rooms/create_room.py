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
  
  if 'roomName' in eventBody:
      room = {
          'uuid': uid,
          'roomName': eventBody['roomName'],
          'created_at': nowtime,
          'updated_at': nowtime
      }
      room_table.put_item(Item=room)
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": json.dumps(room)
      }
  else:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 400,
          "body": "{\"errorMessage\": \"Invalid Parameters: Missing roomName\"}"
      }

  
  return response
