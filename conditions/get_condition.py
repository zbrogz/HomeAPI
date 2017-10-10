import os
import boto3
import json
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def get_condition(uuid):
  print("Getting Condition")
  table_name = os.environ['CONDITIONS_TABLE_NAME']
  conditions_table = boto3.resource('dynamodb').Table(table_name)
    
  response = conditions_table.query(KeyConditionExpression=Key('uuid').eq(uuid))
  if len(response['Items'])==1:
    return response['Items'][0]
  else:
    return None
    
def lambda_handler(event, context):
  print("Starting Get Conditions Lambda Function")
  
  if event['pathParameters'] and 'conditionID' in event['pathParameters']:
    uuid = event['pathParameters']['conditionID']
    condition = get_condition(uuid)
    if condition == None:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 404,
          "body": "{\"errorMessage\": \"Condition not found.\"}"
      }
    else:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": json.dumps(condition)
      }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing UUID.\"}"
    }
  
  return response