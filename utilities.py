import boto3
import os
#Common Utilities  
class ParameterException(Exception):
  pass
  
def get_table_ref(table_name):
  return boto3.resource('dynamodb').Table(os.environ[table_name+'_TABLE_NAME'])