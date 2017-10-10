import os
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

def get_all_conditions():
  print("Getting Conditions")
  
  table_name = os.environ['CONDITIONS_TABLE_NAME']
  conditions_table = boto3.resource('dynamodb').Table(table_name)
  
  
  result = conditions_table.scan()
  conditions = result['Items']
  while 'LastEvaluateKey' in result:
          result = conditions_table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          conditions += result['Items']
          
  return conditions

def lambda_handler(event, context):
  print(" Starting Get Conditions Lambda Function")
  conditions = get_all_conditions()
  
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(conditions)
  }
  
  return response