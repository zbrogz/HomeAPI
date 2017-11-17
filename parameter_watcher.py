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
  cmpParamValues = load_params(condition['cmpParamIDs'])
  return eval(condition['expression'])

def fire_action(actionID):
  print("Firing Action")
  action = load_action(actionID)
  for actionCommand in action['actionCommands']:
    cmpParamValues = load_params(actionCommand['cmpParamIDs'])
    update_parameter(actionCommand['paramID'], eval(actionCommand['expression']))

def load_action(actionID):
  if not actionID:
    raise BadConditionException("Missing actionID")
  response = actions_table().query(KeyConditionExpression=Key('uuid').eq(actionID))
  if len(response['Items'])!=1:
    raise BadConditionException("Action not found")
  return response['Items'][0]

def load_params(paramIDs):
  paramValues = []
  for paramID in paramIDs:
    param = params_table().query(KeyConditionExpression=Key('uuid').eq(paramID))   
    if param['paramType'] == "string":
      paramValues.append(param['paramValue'])
    elif param['paramType'] == "number":_
      paramValues.append(int(param['paramValue']))
    elif param['paramType'] == "bool":
      paramValues.append(param['paramValue'] in 'true')
    else:
      raise BadConditionException("Bad parameter type")

  return paramValues

def update_parameter(paramID, paramValue):
  nowtime = datetime.now().strftime('%x-%X')
  params_table().update_item(
        Key={'uuid': paramID},
        UpdateExpression="set paramValue = :v, updated_at = :t",
        ExpressionAttributeValues={':v': paramValue, ':t': nowtime}
  )
      


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