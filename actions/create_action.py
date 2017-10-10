import os
import boto3
import json
from datetime import datetime
from uuid import uuid4 as uuid

def lambda_handler(event, context):
    print("Starting Create Action Lambda Function")
    
    table_name = os.environ['ACTIONS_TABLE_NAME']
    action_table = boto3.resource('dynamodb').Table(table_name)
    
    eventBody = json.loads(event['body'])
    uid = uuid().hex
    nowtime = datetime.now().strftime('%x-%X')
    print("UID is "+uid)
    
    #default error response
    response = {
        "isBase64Encoded": "false",
        "statusCode": 400,
        "body": "{\"errorMessage\": \"Invalid Parameters: actionName and actionCommands required.\"}"
    }
    
    if 'action' in eventBody:
      newAction = eventBody['action']
      if 'actionName' in newAction and 'actionCommands' in newAction:
        #Validate all commands before create
        for command in newAction['actionCommands']:
          if not 'paramID' in command or not 'paramValue' in command:
            return response
        
        action = {
            'uuid': uid,
            'actionName': newAction['actionName'],
            'actionCommands': newAction['actionCommands'],
            'created_at': nowtime,
            'updated_at': nowtime
        }
        
        action_table.put_item(Item=action)
            
        response = {
            "isBase64Encoded": "false",
            "statusCode": 200,
            "body": "{\"action\": "+json.dumps(action)+" }"
        }
    
    return response
