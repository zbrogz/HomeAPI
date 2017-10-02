import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    print(" Starting Update Device Lambda Function")
    
    table_name = os.environ['DEVICES_TABLE_NAME']
    device_table = boto3.resource('dynamodb').Table(table_name)
    
    eventBody = json.loads(event['body'])

    nowtime = datetime.now().strftime('%x-%X')
    
    #default to error response
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameters\"}"
    }
    
    
    if 'device' in eventBody and event['pathParameters'] and 'deviceID' in event['pathParameters']:
        uuid = event['pathParameters']['deviceID']
        
        device = eventBody['device']
        updateExpressions=[]
        attributeValues={}
        if 'deviceName' in device:
          updateExpressions.append("deviceName = :n")
          attributeValues[':n'] = device['deviceName']
        if 'deviceType' in device:
          updateExpressions.append("deviceType = :t")
          attributeValues[':t'] = device['deviceType']
        if 'roomID' in device:
          updateExpressions.append("roomID = :r")
          attributeValues[':r'] = device['roomID']
          
        if len(updateExpressions) < 1:
          #error if not updating anything
          return response
        
        #update time
        updateExpressions.append("updated_at = :u")
        attributeValues[':u'] = datetime.now().strftime('%x-%X')
        
        updateExpressionStr = "set "+(",".join(updateExpressions))
        
        print(updateExpressionStr)
        
        result = device_table.update_item(
              Key={'uuid': uuid},
              UpdateExpression=updateExpressionStr,
              ExpressionAttributeValues=attributeValues)
        response = {
            "isBase64Encoded": "false",
            "statusCode": 200,
            "body": "{\"message\": \"Device updated\"}"
        }
    
    return response
