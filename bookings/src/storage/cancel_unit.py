import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StorageUnits')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    facility_id = body['facility_id']
    unit_id = body['unit_id']
    customer_id = body['customer_id']

    # Update the unit's status to "Cancelling"
    table.update_item(
        Key={
            'facility_id': facility_id,
            'unit_id': unit_id
        },
        UpdateExpression="set #status = :status, customer_id = :customer_id",
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':status': 'Cancelling',
            ':customer_id': customer_id
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Unit cancellation processed"})
    }
