import os
import boto3
import json
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def delete_room(uuid):
  print("Deleting Rooms")
  table_name = os.environ['ROOMS_TABLE_NAME']
  rooms_table = boto3.resource('dynamodb').Table(table_name)
    
  response = rooms_table.delete_item(Key={'uuid': uuid})

    
def lambda_handler(event, context):
  print("Starting Get Room Lambda Function")
  
  if event['pathParameters'] and 'roomID' in event['pathParameters']:
    uuid = event['pathParameters']['roomID']
    print("UUID: "+uuid)
    delete_room(uuid)
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"message\": \"Room Deleted.\"}"
    }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing UUID.\"}"
    }
  
  return response
  