import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
  print("Starting Update Parameters Lambda Function")
  
  table_name = os.environ['PARAMETERS_TABLE_NAME']
  parameters_table = boto3.resource('dynamodb').Table(table_name)
  
  eventBody = json.loads(event['body'])

  nowtime = datetime.now().strftime('%x-%X')
  
  #default to error response
  response = {
      "isBase64Encoded": "false",
      "statusCode": 400,
      "body": "{\"errorMessage\": \"Invalid Parameters\"}"
  }
  
    
  if event['pathParameters'] and 'paramID' in event['pathParameters'] and 'paramValue' in eventBody:
    parameters_table.update_item(
      Key={'uuid': event['pathParameters']['paramID']},
      UpdateExpression="set paramValue = :v, updated_at = :t",
      ExpressionAttributeValues={':v': eventBody['paramValue'], ':t': nowtime}
    )
      
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"Messsage\": \"Parameter Updated\"}"
    }
    
  return response