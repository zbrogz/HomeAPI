import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def validateParamters(parameters):
  for parameter in parameters:
    if not 'paramID' in parameter or not 'paramValue' in parameter:
      return False
  
  return True

def lambda_handler(event, context):
  print(" Starting Update Action Lambda Function")
  
  table_name = os.environ['ACTIONS_TABLE_NAME']
  actions_table = boto3.resource('dynamodb').Table(table_name)
  
  eventBody = json.loads(event['body'])

  nowtime = datetime.now().strftime('%x-%X')
  
  #default error response
  response = {
      "isBase64Encoded": "false",
      "statusCode": 400,
      "body": "{\"errorMessage\": \"Invalid Parameters: Missing roomName\"}"
  }
  
  if 'action' in eventBody and event['pathParameters'] and 'actionID' in event['pathParameters']:
      uuid = event['pathParameters']['actionID']
      
      action = eventBody['action']
      updateExpressions=[]
      attributeValues={}
      if 'actionName' in action:
        updateExpressions.append("actionName = :n")
        attributeValues[':n'] = action['actionName']
      if 'actionCommands' in action:
        if not validateParamters(action['actionCommands']):
          #new parameters do not validate, return error response
          return response
        else:
          updateExpressions.append("actionCommands = :c")
          attributeValues[':c'] = action['actionCommands']
        
      if len(updateExpressions) < 1:
        #error if not updating anything
        return response
      
      #update time
      updateExpressions.append("updated_at = :u")
      attributeValues[':u'] = datetime.now().strftime('%x-%X')
      
      updateExpressionStr = "set "+(",".join(updateExpressions))
      
      print(updateExpressionStr)
      
      result = actions_table.update_item(
            Key={'uuid': uuid},
            UpdateExpression=updateExpressionStr,
            ExpressionAttributeValues=attributeValues)
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": "{\"message\": \"Action updated\"}"
      }
  
  return response
