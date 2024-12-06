import json
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
bookings_table = dynamodb.Table(os.environ['BOOKINGS_TABLE'])
storage_units_table = dynamodb.Table(os.environ['STORAGE_UNITS_TABLE'])

def lambda_handler(event, context):
    """
    Main handler for updating booking status to 'Cancelling'.
    """
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')

    if http_method == 'PUT' and '/bookings/' in path:
        booking_id = path.split('/')[-1]
        return cancel_booking(booking_id)
    else:
        return respond(400, {'message': 'Invalid operation'})

def cancel_booking(booking_id):
    """Set the booking status to 'Cancelling' and update the storage unit status."""
    try:
        # Retrieve booking details
        booking_response = bookings_table.get_item(Key={'booking_id': booking_id})
        if 'Item' not in booking_response:
            return respond(404, {'message': 'Booking not found'})

        booking = booking_response['Item']
        if booking['status'] != 'Reserved':
            return respond(400, {'message': 'Only reserved bookings can be cancelled'})

        # Update booking status to 'Cancelling'
        bookings_table.update_item(
            Key={'booking_id': booking_id},
            UpdateExpression="SET #status = :cancelling, #updated_at = :timestamp",
            ExpressionAttributeNames={
                '#status': 'status',
                '#updated_at': 'updated_at'
            },
            ExpressionAttributeValues={
                ':cancelling': 'Cancelling',
                ':timestamp': datetime.now().isoformat()
            }
        )

        # Update the storage unit status to 'Available'
        storage_units_table.update_item(
            Key={'unit_id': booking['unit_id']},
            UpdateExpression="SET #status = :available",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':available': 'Available'}
        )

        return respond(200, {'message': f'Booking {booking_id} set to Cancelling, unit released'})

    except ClientError as e:
        return respond(500, {'error': str(e)})
    except Exception as e:
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
