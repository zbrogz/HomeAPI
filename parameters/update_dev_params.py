import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
  print("Starting Update Device Parameters Lambda Function")
  
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
  
    
  if 'parameters' in eventBody:
    parameters = eventBody['parameters']
    #Verify correct parameters
    for parameter in parameters:
      if not 'uuid' in parameter or not 'paramValue' in parameter:
        return response

    for parameter in parameters:
      parameters_table.update_item(
        Key={'uuid': parameter['uuid']},
        UpdateExpression="set paramValue = :v, updated_at = :t",
        ExpressionAttributeValues={':v': parameter['paramValue'], ':t': nowtime}
      )
      
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": "{\"Messsage\": \"Parameters Updated\"}"
      }
      
    
    return response
