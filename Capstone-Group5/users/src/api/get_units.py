import boto3
import json

dynamodb = boto3.resource('dynamodb')
units_table = dynamodb.Table('StorageUnits')

def lambda_handler(event, context):
    try:
        # Scan the DynamoDB table for all units
        response = units_table.scan(FilterExpression="availability = :a", ExpressionAttributeValues={":a": "available"})
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'])
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

