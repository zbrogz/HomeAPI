from utilities import ParameterException, get_table_ref
import boto3
import os
import json
from datetime import datetime
from uuid import uuid4 as uuid
from boto3.dynamodb.conditions import Key

#Action Methods

def create_room(roomData):
  print("Creating Room")
  uid = uuid().hex
  nowtime = datetime.now().strftime('%x-%X')
  print("UID is "+uid)
  
  if 'roomName' in roomData:
      room = {
          'uuid': uid,
          'roomName': roomData['roomName'],
          'created_at': nowtime,
          'updated_at': nowtime
      }
      rooms_table().put_item(Item=room)
      response = {
          "isBase64Encoded": "false",
          "statusCode": 200,
          "body": json.dumps(room)
      }
  else:
      raise ParameterException(400, "Invalid Parameters: Missing roomName")  
  return response

def get_room(roomID):
  print("Getting Room")
  if not roomID:
    raise ParameterException(400, "Invalid Parameter: Missing roomID in path")
  room = load_room(roomID)
  if room == None:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 404,
        "body": "{\"errorMessage\": \"Room not found.\"}"
    }
  else:
    response = {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": json.dumps(room)
    }
  return response

def delete_room(roomID):
  print("Deleting Room")
  if not roomID:
    raise ParameterException(400 , "Invalid Paramters: Missing roomID in path")
  response = rooms_table().delete_item(Key={'uuid': roomID})
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"message\": \"Room Deleted.\"}"
  }

  return response

def get_rooms():
  print("Getting All Rooms")
  table = rooms_table()
  result = table.scan()
  rooms = result['Items']
  while 'LastEvaluateKey' in result:
          result = table.scan(ExclusiveStartKey=result['LastEvaluateKey'])
          rooms += result['Items']
          
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": json.dumps(rooms)
  }
       
  return response

def update_room(roomID,roomData):
  print(" Starting Update Room Lambda Function")
  if not roomID:
    raise ParameterException(400, "Invalid Parameter: Missing roomID in path")
  if not 'roomName' in roomData:
    raise ParameterException(400, "Invalid Parameters: Missing roomName")
  
  nowtime = datetime.now().strftime('%x-%X')
  
  result = rooms_table().update_item(
            Key={'uuid': roomID},
            UpdateExpression="set roomName = :n",
            ExpressionAttributeValues={':n': roomData['roomName']})
  response = {
      "isBase64Encoded": "false",
      "statusCode": 200,
      "body": "{\"message\": \"Room updated\"}"
  }
  return response

#Helper Methods 

def rooms_table():
  return get_table_ref("ROOMS")

def get_roomID(event):
  if event['pathParameters'] and 'roomID' in event['pathParameters']:
    return event['pathParameters']['roomID']
  else:
    return None
  
def load_room(uuid):
  print("Getting Room")
  response = rooms_table().query(KeyConditionExpression=Key('uuid').eq(uuid))
  if len(response['Items'])==1:
    return response['Items'][0]
  else:
    return None

def lambda_handler(event, context):
  print("Starting Rooms Lambda Function")
  try:
    if event['httpMethod'] == "GET":
      roomID = get_roomID(event)
      if roomID:
        return get_room(roomID)
      else:
        return get_rooms()
    elif event['httpMethod'] == "POST":
      return create_room(json.loads(event['body']))
    elif event['httpMethod'] == "DELETE":
      roomID = get_roomID(event)
      return delete_room(roomID)
    elif event['httpMethod'] == 'PATCH':
      roomID = get_roomID(event)
      return update_room(roomID,json.loads(event['body']))
  except ParameterException as e:
    response = {
        "isBase64Encoded": "false",
        "statusCode": e.args[0],
        "body": "{\"errorMessage\": \""+e.args[1]+".\"}"
    }
    return response
    