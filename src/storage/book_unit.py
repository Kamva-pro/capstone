import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('StorageUnits')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    facility_id = body['facility_id']
    unit_id = body['unit_id']
    customer_id = body['customer_id']
    booking_start_date = body['booking_start_date']
    booking_end_date = body['booking_end_date']

    # Update the unit's status to "Reserved"
    table.update_item(
        Key={
            'facility_id': facility_id,
            'unit_id': unit_id
        },
        UpdateExpression="set #status = :status, customer_id = :customer_id, booking_start_date = :start, booking_end_date = :end",
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':status': 'Reserved',
            ':customer_id': customer_id,
            ':start': booking_start_date,
            ':end': booking_end_date
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Unit booked successfully"})
    }
