import os
import boto3
import json
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def get_room(uuid):
  print("Getting Rooms")
  table_name = os.environ['ROOMS_TABLE_NAME']
  rooms_table = boto3.resource('dynamodb').Table(table_name)
    
  response = rooms_table.query(KeyConditionExpression=Key('uuid').eq(uuid))
  print("Rooms: "+str(len(response['Items'])))
  if len(response['Items'])==1:
    return response['Items'][0]
  else:
    return None
    
def lambda_handler(event, context):
  print("Starting Get Room Lambda Function")
  
  if event['pathParameters'] and 'roomID' in event['pathParameters']:
    uuid = event['pathParameters']['roomID']
    print("UUID: "+uuid)
    room = get_room(uuid)
    if room == None:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 404,
          "body": "{\"errorMessage\": \"Room not found.\"}"
      }
    else:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": json.dumps(room)
      }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing UUID.\"}"
    }
  
  return response
  