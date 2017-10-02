import os
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

def get_all_devices():
  print("Getting Devices")
  
  table_name = os.environ['DEVICES_TABLE_NAME']
  devices_table = boto3.resource('dynamodb').Table(table_name)
  
  
  result = devices_table.scan()
  devices = result['Items']
  while 'LastEvaluateKey' in result:
          result = devices_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          devices += result['Items']
          
  return devices

def get_room_devices(roomID):
  print("Getting Room Devices")
  
  table_name = os.environ['DEVICES_TABLE_NAME']
  devices_table = boto3.resource('dynamodb').Table(table_name)
  
  #This is inefficient because we are scaning the full table, and then removing results.
  #A query would be better, but then we would need a local secondary index.
  #Since there will be a limited number of devices (<50), I am not worrying about it.
  result = devices_table.scan(FilterExpression=Key('roomID').eq(roomID))
  devices = result['Items']
  while 'LastEvaluateKey' in result:
          result = devices_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          devices += result['Items']
          
  return devices

def lambda_handler(event, context):
  print(" Starting Get Rooms Lambda Function")
  
  if event['pathParameters'] and 'roomID' in event['pathParameters']:
    roomID = event['pathParameters']['roomID']
    devices = get_room_devices(roomID)
  else:
    devices = get_all_devices()
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(devices)
  }
  
  return response