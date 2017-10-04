import os
import boto3
import json
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def get_device(deviceID):
  print("Getting Device")
  table_name = os.environ['DEVICES_TABLE_NAME']
  device_table = boto3.resource('dynamodb').Table(table_name)
    
  response = device_table.query(KeyConditionExpression=Key('uuid').eq(deviceID))
  print("Device: "+str(len(response['Items'])))
  if len(response['Items'])==1:
    return response['Items'][0]
  else:
    return None

def get_parameters(deviceID):
  print("Getting Parameters")
  table_name = os.environ['PARAMETERS_TABLE_NAME']
  parameters_table = boto3.resource('dynamodb').Table(table_name)
  
  result = parameters_table.scan(FilterExpression=Key('deviceID').eq(deviceID))
  parameters = result['Items']
  while 'LastEvaluateKey' in result:
    result = parameters_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
    parameters += result['Items']
  return parameters
      
    
def lambda_handler(event, context):
  print("Starting Get Device Lambda Function")
  
  if event['pathParameters'] and 'deviceID' in event['pathParameters']:
    uuid = event['pathParameters']['deviceID']
    print("UUID: "+uuid)
    device = get_device(uuid)
    if device == None:
      response = {
          "isBase64Encoded": "false",
          "statusCode": 404,
          "body": "{\"errorMessage\": \"Device not found.\"}"
      }
    else:
      parameters = get_parameters(uuid)
      device['parameters'] = parameters
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": json.dumps(device)
      }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing UUID.\"}"
    }
  
  return response
  