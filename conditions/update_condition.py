import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
  print(" Starting Update Conditions Lambda Function")
  
  table_name = os.environ['CONDITIONS_TABLE_NAME']
  conditions_table = boto3.resource('dynamodb').Table(table_name)
  
  eventBody = json.loads(event['body'])

  nowtime = datetime.now().strftime('%x-%X')
  
  #default error response
  response = {
      "isBase64Encoded": "false",
      "statusCode": 400,
      "body": "{\"errorMessage\": \"Invalid Parameters: Missing roomName\"}"
  }
  
  if 'condition' in eventBody and event['pathParameters'] and 'conditionsID' in event['pathParameters']:
      uuid = event['pathParameters']['conditionID']
      
      condition = eventBody['condition']
      updateExpressions=[]
      attributeValues={}
      if 'conditionName' in condition:
        updateExpressions.append("conditionName = :n")
        attributeValues[':n'] = condition['conditionName']
      if 'actionID' in condition:
        updateExpressions.append("actionID = :a")
        attributeValues[':a'] = condition['actionID']
      if 'paramID' in condition:
        updateExpressions.append("paramID = :p")
        attributeValues[':p'] = condition['paramID']
      if 'comparision' in condition:
        updateExpressions.append("comparision = :c")
        attributeValues[':c'] = condition['comparision']
      if 'comparisionValue' in condition:
        updateExpressions.append("comparisionValue = :v")
        attributeValues[':v'] = condition['comparisionValue']      
        
      if len(updateExpressions) < 1:
        #error if not updating anything
        return response
      
      #update time
      updateExpressions.append("updated_at = :u")
      attributeValues[':u'] = datetime.now().strftime('%x-%X')
      
      updateExpressionStr = "set "+(",".join(updateExpressions))
      
      print(updateExpressionStr)
      
      result = conditions_table.update_item(
            Key={'uuid': uuid},
            UpdateExpression=updateExpressionStr,
            ExpressionAttributeValues=attributeValues)
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": "{\"message\": \"Condition updated\"}"
      }
  
  return response
