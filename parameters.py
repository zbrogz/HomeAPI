from utilities import ParameterException, get_table_ref
import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid
from boto3.dynamodb.conditions import Key


#Actions

def get_parameter(paramID, deviceID):
  print("Getting Parameter.")
  parameter = load_parameter(paramID,deviceID)

  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(parameter)
  }
  return response
  
def update_parameter(paramID, deviceID, paramData):
  print("Updating Parameter")
  parameter = load_parameter(paramID,deviceID)
  
  if not 'paramValue' in paramData:
    raise ParameterException(400, "Invalid parameters: Missing paramValue")
  
  nowtime = datetime.now().strftime('%x-%X')
  params_table().update_item(
    Key={'uuid': paramID},
    UpdateExpression="set paramValue = :v, updated_at = :t",
    ExpressionAttributeValues={':v': paramData['paramValue'], ':t': nowtime}
  )  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"Messsage\": \"Parameter Updated\"}"
  }
  return response

def update_device_params(deviceID, params):
  print("Updating Device Parameters")


  nowtime = datetime.now().strftime('%x-%X')
  #verify params
  for param in params:
    if not 'uuid' in param or not 'paramValue' in param:
      raise ParameterException(400, "Invalid Paramters: missing uuid or paramValue")

  for param in params:
    params_table().update_item(
      Key={'uuid': param['uuid']},
      UpdateExpression="set paramValue = :v, updated_at = :t",
      ExpressionAttributeValues={':v': param['paramValue'], ':t': nowtime}
    )
      
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"Messsage\": \"Parameters Updated\"}"
    }
    return response

#Helper Methods

def load_parameter(paramID, deviceID):
  if not paramID:
    raise ParameterException(404, "Missing ParameterID")
  response = params_table().query(KeyConditionExpression=Key('uuid').eq(paramID))
  if len(response['Items'])!=1:
    raise ParameterException(404, "Parameter Not Found")
  parameter = response['Items'][0]
  if deviceID and parameter['deviceID'] != deviceID:
    #wrong device ID
    raise ParameterException(404, "Device parameter not found")
  return parameter

def params_table():
  return get_table_ref('PARAMETERS')

def get_deviceID(event):
  if event['pathParameters'] and 'deviceID' in event['pathParameters']:
    return event['pathParameters']['deviceID']
  else:
    return None

def get_paramID(event):
  if event['pathParameters'] and 'paramID' in event['pathParameters']:
    return event['pathParameters']['paramID']
  else:
    return None


def lambda_handler(event, context):
  print("Starting Parameters Lambda Function")
  try:
    if event['httpMethod'] == "GET":
      paramID = get_paramID(event)
      deviceID = get_deviceID(event) #can be misisng
      return get_parameter(paramID,deviceID)
      #Don't need device id unless I want to add validation after
    elif event['httpMethod'] == "POST":
      deviceID = get_deviceID(event)
      return update_device_params(deviceID,json.loads(event['body']))
    elif event['httpMethod'] == 'PATCH':
      paramID = get_paramID(event)
      deviceID = get_deviceID(event)
      return update_parameter(paramID,deviceID,json.loads(event['body']))
  except ParameterException as e:
    response = {
        "isBase64Encoded": "false",
        "statusCode": e.args[0],
        "body": "{\"errorMessage\": \""+e.args[1]+".\"}"
    }
    return response