from utilities import ParameterException, get_table_ref
import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid
from boto3.dynamodb.conditions import Key

#Actions
def create_condition(conditionData):
  print("Creating Condition ")
  if not 'conditionName' in conditionData:
    raise ParameterException(400, "Invalid Parameters: Missing conditionName")
  if not 'actionID' in conditionData: 
    raise ParameterException(400, "Invalid Parameters: Missing actoinID")
  if not 'paramID' in conditionData:
    raise ParameterException(400, "Invalid Parameters: Missing paramID")
  if not 'comparison' in conditionData:
    raise ParameterException(400, "Invalid Parameters: Missing comparison")
  if not 'comparisonValue' in conditionData:
    raise ParameterException(400, "Invalid Parameters: Missing comparisonValue")
  
  uid = uuid().hex
  nowtime = datetime.now().isoformat()
  condition = {
      'uuid': uid,
      'actionID': conditionData['actionID'],
      'conditionName': conditionData['conditionName'],
      'paramID': conditionData['paramID'],
      'comparison': conditionData['comparison'],
      'comparisonValue': conditionData['comparisonValue'],
      'created_at': nowtime,
      'updated_at': nowtime
  }    
  conditions_table().put_item(Item=condition)

  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"condition\": "+json.dumps(condition)+" }"
  }
    
  return response

def get_condition(conditionID):
  print("Getting Condition")
  condition = load_condition(conditionID)
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(condition)
  }
  return response

def get_conditions():
  print("Getting Condition")
  result = conditions_table().scan()
  conditions = result['Items']
  while 'LastEvaluateKey' in result:
          result = conditions_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          conditions += result['Items']
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(conditions)
  }
          
  return response

def update_condition(conditionID,conditionData):
  print("Updating Condition")
  load_condition(conditionID)#verifies condition exists

  updateExpressions=[]
  attributeValues={}
  if 'conditionName' in conditionData:
    updateExpressions.append("conditionName = :n")
    attributeValues[':n'] = conditionData['conditionName']
  if 'actionID' in conditionData:
    updateExpressions.append("actionID = :a")
    attributeValues[':a'] = conditionData['actionID']
  if 'paramID' in conditionData:
    updateExpressions.append("paramID = :p")
    attributeValues[':p'] = conditionData['paramID']
  if 'comparison' in conditionData:
    updateExpressions.append("comparison = :c")
    attributeValues[':c'] = conditionData['comparison']
  if 'comparisonValue' in conditionData:
    updateExpressions.append("comparisonValue = :v")
    attributeValues[':v'] = conditionData['comparisonValue']      
    
  if len(updateExpressions) < 1:
    #error if not updating anything
    raise ParameterException(400, "Nothing to update")
  
  #update time
  updateExpressions.append("updated_at = :u")
  attributeValues[':u'] = datetime.now().isoformat()
  
  updateExpressionStr = "set "+(",".join(updateExpressions))
  
  print(updateExpressionStr)
  
  result = conditions_table().update_item(
        Key={'uuid': conditionID},
        UpdateExpression=updateExpressionStr,
        ExpressionAttributeValues=attributeValues)
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"message\": \"Condition updated\"}"
  }
  
  return response  
  
def delete_condition(conditionID):
  print("Deleting Condition")
  condition = load_condition(conditionID) #makes sure action exists
  conditions_table().delete_item(Key={'uuid': conditionID})
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"message\": \"Action Deleted.\"}"
  }
  return response 
#Helper Methods

def load_condition(conditionID):
  if not conditionID:
    raise ParameterException(400, "Invalid Parameter: missing conditionID")
    
  response = conditions_table().query(KeyConditionExpression=Key('uuid').eq(conditionID))
  if len(response['Items'])!=1:
    raise ParameterException(404, "Condition not found")
    
  return response['Items'][0]

def get_conditionID(event):
  if event['pathParameters'] and 'conditionID' in event['pathParameters']:
    return event['pathParameters']['conditionID']
  else:
    return None

def conditions_table():
  return get_table_ref('CONDITIONS')


def lambda_handler(event, context):
  print("Starting Conditions Lambda Function")
  try:
    if event['httpMethod'] == "GET":
      conditionID = get_conditionID(event)
      if conditionID:
        return get_condition(conditionID)
      else:
        return get_conditions()
    elif event['httpMethod'] == "POST":
      return create_condition(json.loads(event['body']))
    elif event['httpMethod'] == "DELETE":
      conditionID = get_conditionID(event)
      return delete_condition(conditionID)
    elif event['httpMethod'] == 'PATCH':
      conditionID = get_conditionID(event)
      return update_condition(conditionID,json.loads(event['body']))
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