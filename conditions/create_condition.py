import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid

def lambda_handler(event, context):
    print("Starting Create Condition Lambda Function")
    
    table_name = os.environ['CONDITIONS_TABLE_NAME']
    condition_table = boto3.resource('dynamodb').Table(table_name)
    
    eventBody = json.loads(event['body'])
    uid = uuid().hex
    nowtime = datetime.now().strftime('%x-%X')
    print("UID is "+uid)
    
    #default error response
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameters: conditionName, actionID, paramID, comparision, and comparisionValue required.\"}"
    }
    
    if 'condition' in eventBody:
      newCondition = eventBody['condition']
      if 'conditionName' in newCondition and 'actionID' in newCondition and 'paramID' in newCondition and 'comparision' in newCondition and 'comparisionValue' in newCondition:
        condition = {
            'uuid': uid,
            'actionID': newCondition['actionID'],
            'conditionName': newCondition['conditionName'],
            'paramID': newCondition['paramID'],
            'comparision': newCondition['comparision'],
            'compValue': newCondition['comparisionValue'],
            'created_at': nowtime,
            'updated_at': nowtime
        }
        

        condition_table.put_item(Item=condition)

      
        response = {
            "isBase64Encoded": "false",
            "statusCode": 200,
            "body": "{\"condition\": "+json.dumps(condition)+" }"
        }

    
    return response