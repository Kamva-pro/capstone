import json
import os
import boto3

# Prepare DynamoDB client
TABLE_NAME = os.getenv('TABLE_NAME', None)
dynamodb = boto3.resource('dynamodb')
ddbTable = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    route_key = f"{event['httpMethod']} {event['resource']}"

    # Set default response, override with data from DynamoDB if any
    response_body = {'Message': 'Unsupported route'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    try:
        # Handle GET request for listing all storage units
        if route_key == 'GET /units':
            # Scan DynamoDB to retrieve all storage units
            ddb_response = ddbTable.scan(Select='ALL_ATTRIBUTES')
            response_body = ddb_response['Items']  # Return the list of items
            status_code = 200

    except Exception as err:
        status_code = 400
        response_body = {'Error:': str(err)}
        print(str(err))

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
