import json
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
bookings_table = dynamodb.Table(os.environ['BOOKINGS_TABLE'])
users_table = dynamodb.Table(os.environ['USERS_TABLE'])
storage_units_table = dynamodb.Table(os.environ['STORAGE_UNITS_TABLE'])

def lambda_handler(event, context):
    """
    Main handler for creating bookings.
    """
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')

    if http_method == 'POST' and path == '/bookings':
        return create_booking(event)
    else:
        return respond(400, {'message': 'Invalid operation'})

def create_booking(event):
    """Create a new booking."""
    try:
        # Parse request body
        booking_data = json.loads(event['body'])
        required_fields = ['userid', 'unit_id', 'start_date', 'end_date']

        # Ensure required fields are present
        if not all(field in booking_data for field in required_fields):
            return respond(400, {'message': 'Missing required fields'})

        # Check if user exists
        user_response = users_table.get_item(Key={'userid': booking_data['userid']})
        if 'Item' not in user_response:
            return respond(404, {'message': 'User not found'})

        # Check if storage unit exists and is available
        unit_response = storage_units_table.get_item(Key={'unit_id': booking_data['unit_id']})
        if 'Item' not in unit_response or unit_response['Item'].get('status') != 'Available':
            return respond(404, {'message': 'Storage unit not available or does not exist'})

        # Generate booking ID and prepare booking item
        booking_id = f"booking-{int(datetime.now().timestamp())}"
        booking_item = {
            'booking_id': booking_id,
            'userid': booking_data['userid'],
            'unit_id': booking_data['unit_id'],
            'start_date': booking_data['start_date'],
            'end_date': booking_data['end_date'],
            'status': 'Reserved',
            'created_at': datetime.now().isoformat()
        }

        # Save booking to the BookingsTable
        bookings_table.put_item(Item=booking_item)

        # Update the storage unit status to 'Reserved'
        storage_units_table.update_item(
            Key={'unit_id': booking_data['unit_id']},
            UpdateExpression="SET #st = :reserved",
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={':reserved': 'Reserved'}
        )

        return respond(201, {'message': 'Booking created successfully', 'booking': booking_item})

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
