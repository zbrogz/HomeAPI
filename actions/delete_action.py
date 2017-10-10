import os
import boto3
import json
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def delete_action(uuid):
  print("Deleting Action")
  table_name = os.environ['ACTIONS_TABLE_NAME']
  actions_table = boto3.resource('dynamodb').Table(table_name)
    
  response = actions_table.delete_item(Key={'uuid': uuid})

    
def lambda_handler(event, context):
  print("Starting Delete Action Lambda Function")
  
  if event['pathParameters'] and 'actionID' in event['pathParameters']:
    uuid = event['pathParameters']['actionID']

    delete_action(uuid)
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"message\": \"Action Deleted.\"}"
    }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing UUID.\"}"
    }
  
  return response
  