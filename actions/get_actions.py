import os
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

def get_all_actions():
  print("Getting Actions")
  
  table_name = os.environ['ACTIONS_TABLE_NAME']
  actions_table = boto3.resource('dynamodb').Table(table_name)
  
  
  result = actions_table.scan()
  actions = result['Items']
  while 'LastEvaluateKey' in result:
          result = actions_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          actions += result['Items']
          
  return actions

def lambda_handler(event, context):
  print(" Starting Get Actions Lambda Function")
  actions = get_all_actions()
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(actions)
  }
  
  return response