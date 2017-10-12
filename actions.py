from utilities import ParameterException, get_table_ref
import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid
from boto3.dynamodb.conditions import Key

#HTTP Actions
def create_action(actionData):
  print("Creating Action")

  if not 'actionName' in actionData or not 'actionCommands' in actionData:
    raise ParameterException(400, "Invalid Parameters: missing actionName or actionCommands")
    #Validate all commands before create
  for command in actionData['actionCommands']:
    if not 'paramID' in command or not 'paramValue' in command:
      raise ParameterException(400, "Invalid actionCommand: missing paramID or paramValue")
  
  uid = uuid().hex
  nowtime = datetime.now().strftime('%x-%X')  
  action = {
      'uuid': uid,
      'actionName': actionData['actionName'],
      'actionCommands': actionData['actionCommands'],
      'created_at': nowtime,
      'updated_at': nowtime
  }
    
  actions_table().put_item(Item=action)
        
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(action)
  }

  return response

def get_action(actionID):
  print("Getting Action")
  
  action = load_action(actionID)
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(action)
  }

  return response

def get_actions():
  print("Getting Actions")
  table = actions_table()
  result = table.scan()
  actions = result['Items']
  while 'LastEvaluateKey' in result:
          result = table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          actions += result['Items']
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(actions)
  }
          
  return response

def delete_action(actionID):
  print("Deleting Action")
  action = load_action(actionID) #makes sure action exists
  actions_table().delete_item(Key={'uuid': actionID})
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"message\": \"Action Deleted.\"}"
  }
  return response 

def update_action(actionID, actionData):
  print("Updating Action")
  if not actionID:
    raise ParameterException(400, "Invalid Parameters: Missing actionID")
  old_action = load_action(actionID) #Makes sure action exists.

  updateExpressions=[]
  attributeValues={}
  if 'actionName' in actionData:
    updateExpressions.append("actionName = :n")
    attributeValues[':n'] = actionData['actionName']
  if 'actionCommands' in actionData:
    if not validateParamters(actionData['actionCommands']):
      #new parameters do not validate
      raise ParameterException(400, "Invalid Action Parameters, missing paramID or paramValue")
    updateExpressions.append("actionCommands = :c")
    attributeValues[':c'] = actionData['actionCommands']
    
  if len(updateExpressions) < 1:
    #error if not updating anything
    raise ParameterException(400, "Invalid Parameters, nothing to update")
  
  #update time
  updateExpressions.append("updated_at = :u")
  attributeValues[':u'] = datetime.now().strftime('%x-%X')
  
  updateExpressionStr = "set "+(",".join(updateExpressions))
  result = actions_table().update_item(
        Key={'uuid': actionID},
        UpdateExpression=updateExpressionStr,
        ExpressionAttributeValues=attributeValues)
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"message\": \"Action updated\"}"
  }
  
  return response

def fire_action(actionID):
  print("Firing Action")
  action = load_action(actionID)
  update_parameters(action['actionCommands'])
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"Message\": \"Action fired.\"}"
  }
  
  return response

#Helper Methods

def load_action(actionID):
  if not actionID:
    raise ParameterException(400, "Invalid parameters: missing actionID")
  response = actions_table().query(KeyConditionExpression=Key('uuid').eq(actionID))
  if len(response['Items'])!=1:
    raise ParameterException(404, "Action not found")
  return response['Items'][0]

def validateParamters(parameters):
  for parameter in parameters:
    if not 'paramID' in parameter or not 'paramValue' in parameter:
      return False
  
  return True

def update_parameters(params):
  nowtime = datetime.now().strftime('%x-%X')
  
  for parameter in params:
      params_table().update_item(
        Key={'uuid': parameter['paramID']},
        UpdateExpression="set paramValue = :v, updated_at = :t",
        ExpressionAttributeValues={':v': parameter['paramValue'], ':t': nowtime}
      )

def get_actionID(event):
  if event['pathParameters'] and 'actionID' in event['pathParameters']:
    return event['pathParameters']['actionID']
  else:
    return None

def actions_table():
  return get_table_ref('ACTIONS')
  
def params_table():
  return get_table_ref('PARAMETERS')

def lambda_handler(event, context):
  print("Starting Devices Lambda Function")
  try:
    if event['httpMethod'] == "GET":
      actionID = get_actionID(event)
      if actionID:
        return get_action(actionID)
      else:
        return get_actions()
    elif event['httpMethod'] == "POST":
      actionID = get_actionID(event)
      if actionID:
        return fire_action(actionID)
      else:
        return create_action(json.loads(event['body']))
    elif event['httpMethod'] == "DELETE":
      actionID = get_actionID(event)
      return delete_action(actionID)
    elif event['httpMethod'] == 'PATCH':
      actionID = get_actionID(event)
      return update_action(actionID,json.loads(event['body']))
  except ParameterException as e:
    response = {
        "isBase64Encoded": "false",
        "statusCode": e.args[0],
        "body": "{\"errorMessage\": \""+e.args[1]+".\"}"
    }
    return response