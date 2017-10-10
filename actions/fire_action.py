import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def get_action(uuid):
  print("Getting Action")
  table_name = os.environ['ACTIONS_TABLE_NAME']
  actions_table = boto3.resource('dynamodb').Table(table_name)
    
  response = actions_table.query(KeyConditionExpression=Key('uuid').eq(uuid))
  print("Actions: "+str(len(response['Items'])))
  if len(response['Items'])==1:
    return response['Items'][0]
  else:
    return None

def update_parameters(parameters):
  table_name = os.environ['PARAMETERS_TABLE_NAME']
  parameters_table = boto3.resource('dynamodb').Table(table_name)
  
  nowtime = datetime.now().strftime('%x-%X')
  
  for parameter in parameters:
      parameters_table.update_item(
        Key={'uuid': parameter['paramID']},
        UpdateExpression="set paramValue = :v, updated_at = :t",
        ExpressionAttributeValues={':v': parameter['paramValue'], ':t': nowtime}
      )
    
def lambda_handler(event, context):
  print("Starting Fire Action Lambda Function")
  
  if event['pathParameters'] and 'actionID' in event['pathParameters']:
    uuid = event['pathParameters']['actionID']
    print("UUID: "+uuid)
    action = get_action(uuid)
    if action == None:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 404,
          "body": "{\"errorMessage\": \"Action not found.\"}"
      }
    else:
      update_parameters(action['actionCommands'])
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": "{\"Message\": \"Action fired.\"}"
      }
      
      return response
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing UUID.\"}"
    }
  
  return response