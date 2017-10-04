import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid

def create_parameters(parameters, deviceID):
  print("Creating device parameters")
  
  table_name = os.environ['PARAMETERS_TABLE_NAME']
  parameters_table = boto3.resource('dynamodb').Table(table_name)
  
  for parameter in parameters:
    if not ('paramName' in parameter and 'paramType' in parameter and 'paramType' in parameter and 'paramActions' in parameter):
      return False
  
  nowtime = datetime.now().strftime('%x-%X')
  with parameters_table.batch_writer() as batch:
    for parameter in parameters:
      uid = uuid().hex
      paramItem = {
        'uuid': uid,
        'deviceID': deviceID,
        'paramName': parameter['paramName'],
        'paramType': parameter['paramType'],
        'paramActions': parameter['paramActions'],
        'created_at': nowtime,
        'updated_at': nowtime
      }
      batch.put_item(Item=paramItem)
  return True

def lambda_handler(event, context):
    print("Starting Create Device Lambda Function")
    
    table_name = os.environ['DEVICES_TABLE_NAME']
    device_table = boto3.resource('dynamodb').Table(table_name)
    
    eventBody = json.loads(event['body'])
    uid = uuid().hex
    nowtime = datetime.now().strftime('%x-%X')
    print("UID is "+uid)
    
    #default error response
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameters: deviceName and deviceType and parameters required.\"}"
    }
    
    if 'device' in eventBody:
      inDevice = eventBody['device']
      if 'deviceName' in inDevice and 'deviceType' in inDevice:
        roomID = None
        if event['pathParameters'] and 'roomID' in event['pathParameters']:
          roomID = event['pathParameters']['roomID']
        device = {
            'uuid': uid,
            'roomID': roomID,
            'deviceName': inDevice['deviceName'],
            'deviceType': inDevice['deviceType'],
            'created_at': nowtime,
            'updated_at': nowtime
        }
        
        if 'parameters' in inDevice:
          #verify parameters before you create device
          if create_parameters(inDevice['parameters'],uid):
            device_table.put_item(Item=device)
            device['path'] = "/devices/"+uid
            
            response = {
                "isBase64Encoded": "false",
                "statusCode": 200,
                "body": "{\"device\": "+json.dumps(device)+" }"
            }
          else:
            response = {
                "isBase64Encoded": "false",
                "statusCode": 400,
                "body": "{\"errorMessage\": \"Invalid Parameters in device parameters.\"}"
            }
    
    return response
