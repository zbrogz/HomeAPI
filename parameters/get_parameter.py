import os
import boto3
import json
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def get_parameter(uuid):
  table_name = os.environ['PARAMETERS_TABLE_NAME']
  parameters_table = boto3.resource('dynamodb').Table(table_name)
    
  response = parameters_table.query(KeyConditionExpression=Key('uuid').eq(uuid))
  if len(response['Items'])==1:
    return response['Items'][0]
  else:
    return None
    
def lambda_handler(event, context):
  print("Starting Get Room Lambda Function")
  
  if event['pathParameters'] and 'paramID' in event['pathParameters']:
    paramID = event['pathParameters']['paramID']
    print("ParamID: "+paramID)
    parameter = get_parameter(paramID)
    if parameter == None or ('deviceID' in event['pathParameters'] and event['pathParameters']['deviceID'] != parameter['deviceID']):
      response = {
          "isBase64Encoded": "false",
          "statusCode": 404,
          "body": "{\"errorMessage\": \"Parameter not found.\"}"
      }
    else:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": json.dumps(parameter)
      }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing UUID.\"}"
    }
  
  return response
  