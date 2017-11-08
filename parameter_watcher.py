from utilities import ParameterException, get_table_ref
#import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key


#Helper Functions
def find_relevant_conditions(paramID):
  print("Looking for conditions")
  ctable = conditions_table()
  
  result = ctable.scan(FilterExpression=Key('paramID').eq(paramID))
  conditions = result['Items']
  while 'LastEvaluateKey' in result:
    result = ctable.scan(ExclusiveStartKey=result['LastEvaluateKey'])
    conditions += result['Items']
  return conditions


def test_condition(condition,paramValue):
  if condition['comparison'] == ">":
    return int(paramValue) > int(condition['comparisonValue'])
  elif condition['comparison'] == "<":
    return int(paramValue) < int(condition['comparisonValue'])
  else:    
    return paramValue == condition['comparisonValue']


def fire_action(actionID):
  print("Firing Action")
  action = load_action(actionID)
  update_parameters(action['actionCommands'])

def update_parameters(params):
  nowtime = datetime.now().strftime('%x-%X')
  
  for parameter in params:
      params_table().update_item(
        Key={'uuid': parameter['paramID']},
        UpdateExpression="set paramValue = :v, updated_at = :t",
        ExpressionAttributeValues={':v': parameter['paramValue'], ':t': nowtime}
      )
  

def load_action(actionID):
  if not actionID:
    raise BadConditionException("Missing actionID")
  response = actions_table().query(KeyConditionExpression=Key('uuid').eq(actionID))
  if len(response['Items'])!=1:
    raise BadConditionException("Action not found")
  return response['Items'][0]

def conditions_table():
  return get_table_ref('CONDITIONS')

def actions_table():
  return get_table_ref('ACTIONS')

def params_table():
  return get_table_ref('PARAMETERS')

#This will get called when any parameter changes. When it does, it will check the conditions and fire
def lambda_handler(event, context):
  print("Starting Parameter Watcher Lambda Function")
  records = event['Records']
  for record in records:
    if record['eventName'] == "MODIFY":
      newImage = record['dynamodb']['NewImage']
      paramID = newImage['uuid']['S']
      paramValue = newImage['paramValue']['S']
      print("ParamID: "+paramID+" ParamValue: "+paramValue)
      conditions = find_relevant_conditions(paramID)
      for condition in conditions:
        try:
          if test_condition(condition,paramValue):
            fire_action(condition['actionID'])
        except ValueError:
          print("Couldn't convert value to int.")
        except BadConditionException as e:
          print("Bad Condition: "+e.args[0])
    else:
      print("Not a modification, ignoring")
  
  return True
  
class BadConditionException(Exception):
  pass