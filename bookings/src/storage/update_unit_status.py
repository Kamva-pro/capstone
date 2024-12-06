import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StorageUnits')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    facility_id = body['facility_id']
    unit_id = body['unit_id']
    status = body['status']

    # Update the unit's status
    table.update_item(
        Key={
            'facility_id': facility_id,
            'unit_id': unit_id
        },
        UpdateExpression="set #status = :status",
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':status': status
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Status updated successfully"})
    }
