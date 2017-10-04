import os
import boto3
import json
from boto3.dynamodb.conditions import Key
#Incase you need the Attr as well.
#from boto3.dynamodb.conditions import Key, Attr

def delete_device_parameters(deviceID):
  print("Deleting Parameters")
  table_name = os.environ['PARAMETERS_TABLE_NAME']
  parameters_table = boto3.resource('dynamodb').Table(table_name)
  
  #This is inefficient because we are scaning the full table, and then removing results.
  #A query would be better, but then we would need a local secondary index.
  #Since there will be a limited number of devices (<50), I am not worrying about it.
  result = parameters_table.scan(FilterExpression=Key('deviceID').eq(deviceID))
  parameters = result['Items']
  while 'LastEvaluateKey' in result:
          result = parameters_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          parameters += result['Items']
          
  for parameter in parameters:
    parameters_table.delete_item(Key={'uuid': parameter['uuid']})
    

def delete_device(deviceID):
  print("Deleting Device")
  table_name = os.environ['DEVICES_TABLE_NAME']
  devices_table = boto3.resource('dynamodb').Table(table_name)
  
  delete_device_parameters(deviceID)  
  
  devices_table.delete_item(Key={'uuid': deviceID})

    
def lambda_handler(event, context):
  print("Starting Delete Device Lambda Function")
  
  if event['pathParameters'] and 'deviceID' in event['pathParameters']:
    uuid = event['pathParameters']['deviceID']
    print("UUID: "+uuid)
    delete_device(uuid)
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"message\": \"Room Deleted.\"}"
    }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameter: missing deviceID.\"}"
    }
  
  return response
  