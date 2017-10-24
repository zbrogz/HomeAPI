from utilities import ParameterException, get_table_ref
import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid
from boto3.dynamodb.conditions import Key

#Actions

#create
def create_device(deviceData,roomID):
    print("Creating Device")
    #ValidateInput
    if not 'deviceName' in deviceData:
      raise ParameterException(400, "Invalid Parameter: Missing deviceName")
    if not 'deviceType' in deviceData:
      raise ParameterException(400, "Invalid Parameter: Missing deviceType")
    if not 'parameters' in deviceData:
      raise ParameterException(400, "Invalid Parameter: Missing parameters")
    
    uid = uuid().hex
    nowtime = datetime.now().isoformat()
    device = {
        'uuid': uid,
        'roomID': roomID,
        'deviceName': deviceData['deviceName'],
        'deviceType': deviceData['deviceType'],
        'created_at': nowtime,
        'updated_at': nowtime
    }

    params = create_parameters(deviceData['parameters'],uid)
    devices_table().put_item(Item=device)
    device['path'] = "/devices/"+uid
    device['parameters'] = params
      
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": json.dumps(device)
    }
  
    return response

#Get Devices
def get_all_devices():
  print("Getting Devices")
  table = devices_table()
  result = table.scan()
  devices = result['Items']
  while 'LastEvaluateKey' in result:
          result = table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          devices += result['Items']
  #load parameters
  for device in devices:
    params = get_parameters(device['uuid'])
    device['parameters'] = params
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(devices)
  }
          
  return response

def get_room_devices(roomID):
  print("Getting Room Devices")
  table = devices_table()
  if not roomID:
    raise ParameterException(400, "Invalid Parameter: Missing roomID")
  #This is inefficient because we are scaning the full table, and then removing results.
  #A query would be better, but then we would need a local secondary index.
  #Since there will be a limited number of devices (<50), I am not worrying about it.
  result = table.scan(FilterExpression=Key('roomID').eq(roomID))
  devices = result['Items']
  while 'LastEvaluateKey' in result:
          result = table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          devices += result['Items']
  
  for device in devices:
    params = get_parameters(device['uuid'])
    device['parameters'] = params
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(devices)
  }
          
  return response

def get_device(deviceID):
  device = load_device(deviceID)
  device['parameters'] = get_parameters(deviceID)
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(device)
  }
          
  return response  

#Update Device

def update_device(deviceID, deviceData):
    print("Updating Device")
    
    if not deviceID:
      raise ParameterException(404, "Missing Device ID")
    
    nowtime = datetime.now().isoformat()
    updateExpressions=[]
    attributeValues={}
    if 'deviceName' in deviceData:
      updateExpressions.append("deviceName = :n")
      attributeValues[':n'] = deviceData['deviceName']
    if 'deviceType' in deviceData:
      updateExpressions.append("deviceType = :t")
      attributeValues[':t'] = deviceData['deviceType']
    if 'roomID' in deviceData:
      updateExpressions.append("roomID = :r")
      attributeValues[':r'] = deviceData['roomID']
    
    print
      
    if len(updateExpressions) < 1:
      #error if not updating anything
      raise ParameterException(400, "Not updating any properties.")
    
    #update time
    updateExpressions.append("updated_at = :u")
    attributeValues[':u'] = datetime.now().isoformat()
    
    updateExpressionStr = "set "+(",".join(updateExpressions))
    
    print(updateExpressionStr)
    print(attributeValues)
    
    result = devices_table().update_item(
          Key={'uuid': deviceID},
          UpdateExpression=updateExpressionStr,
          ExpressionAttributeValues=attributeValues)
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"message\": \"Device updated\"}"
    }
    
    return response

#Delete Device

def delete_device(deviceID):
  print("Deleting Device")
  delete_device_parameters(deviceID)  
  devices_table().delete_item(Key={'uuid': deviceID})
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"message\": \"Device and its parameters Deleted.\"}"
  }
  
  return response 

#Helper Methods 

def get_deviceID(event):
  if event['pathParameters'] and 'deviceID' in event['pathParameters']:
    return event['pathParameters']['deviceID']
  else:
    return None
  
def load_device(uuid):
  print("Getting Device")
  response = devices_table().query(KeyConditionExpression=Key('uuid').eq(uuid))
  if len(response['Items'])==1:
    return response['Items'][0]
  else:
    return None

def create_parameters(parameters, deviceID):
  print("Creating device parameters")
  #Validate Parameters
  for parameter in parameters:
    if not ('paramName' in parameter and 'paramType' in parameter and 'paramActions' in parameter):
      raise ParameterException(400, "Invalid Parameter: Device Parameters do not include all required fields. Need paramName, paramType, paramActions")
  
  parameters_table = get_table_ref('PARAMETERS')
  nowtime = datetime.now().isoformat()
  newParams = []
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
      newParams.append(paramItem)
  return newParams

def get_parameters(deviceID):
  print("Getting Parameters")
  ptable = params_table()
  
  result = ptable.scan(FilterExpression=Key('deviceID').eq(deviceID))
  parameters = result['Items']
  while 'LastEvaluateKey' in result:
    result = ptable.scan(ExclusiveStartKey=result['LastEvaluateKey'])
    parameters += result['Items']
  return parameters

def delete_device_parameters(deviceID):
  print("Deleting Parameters")
  parameters_table = params_table()
  
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

def devices_table():
  return get_table_ref('DEVICES')
  
def params_table():
  return get_table_ref('PARAMETERS')


def lambda_handler(event, context):
  print("Starting Devices Lambda Function")
  try:
    if event['httpMethod'] == "GET":
      deviceID = get_deviceID(event)
      if deviceID:
        return get_device(deviceID)
      else:
        if event['pathParameters'] and 'roomID' in event['pathParameters']:
          return get_room_devices(event['pathParameters']['roomID'])
        else:
          return get_all_devices()
    elif event['httpMethod'] == "POST":
      roomID = event['pathParameters']['roomID'] if event['pathParameters'] and 'roomID' in event['pathParameters'] else None
      return create_device(json.loads(event['body']),roomID)
    elif event['httpMethod'] == "DELETE":
      deviceID = get_deviceID(event)
      return delete_device(deviceID)
    elif event['httpMethod'] == 'PATCH':
      deviceID = get_deviceID(event)
      return update_device(deviceID,json.loads(event['body']))
  except ParameterException as e:
    response = {
        "isBase64Encoded": "false",
        "statusCode": e.args[0],
        "body": "{\"errorMessage\": \""+e.args[1]+".\"}"
    }
    return response
  except json.JSONDecodeError as e:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Malformed JSON: "+e.args[0]+"\"}"
    }
    return response