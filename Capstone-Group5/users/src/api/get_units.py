import json
import os
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
storage_units_table = dynamodb.Table(os.environ['STORAGE_UNITS_TABLE'])

def lambda_handler(event, context):
    """
    Main handler for fetching storage units.
    """
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')

    if http_method == 'GET' and path == '/units':
        return get_all_units()
    elif http_method == 'GET' and '/units/' in path:
        unit_id = path.split('/')[-1]
        return get_unit(unit_id)
    else:
        return respond(400, {'message': 'Invalid operation'})

def get_all_units():
    """Fetch all storage units."""
    try:
        response = storage_units_table.scan()
        return respond(200, {'units': response.get('Items', [])})
    except ClientError as e:
        return respond(500, {'error': str(e)})

def get_unit(unit_id):
    """Fetch a single storage unit by ID."""
    try:
        response = storage_units_table.get_item(Key={'unit_id': unit_id})
        if 'Item' in response:
            return respond(200, response['Item'])
        else:
            return respond(404, {'message': 'Unit not found'})
    except ClientError as e:
        return respond(500, {'error': str(e)})

def respond(status_code, body):
    """Helper function to format HTTP responses."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }
