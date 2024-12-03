import boto3
import json
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
bookings_table = dynamodb.Table('Bookings')
units_table = dynamodb.Table('StorageUnits')

def lambda_handler(event, context):
    try:
        request = json.loads(event['body'])
        unit_id = request['unit_id']
        user_id = request['user_id']

        # Mark unit as booked
        units_table.update_item(
            Key={'unit_id': unit_id},
            UpdateExpression="SET availability = :b",
            ExpressionAttributeValues={":b": "booked"}
        )

        # Create booking record
        booking_id = str(uuid.uuid4())
        booking = {
            'booking_id': booking_id,
            'unit_id': unit_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        bookings_table.put_item(Item=booking)

        return {
            'statusCode': 201,
            'body': json.dumps(booking)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

