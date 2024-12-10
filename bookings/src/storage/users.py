import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import os

# DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Table names from environment variables
USERS_TABLE = os.environ['USERS_TABLE']
STORAGE_UNITS_TABLE = os.environ['STORAGE_UNITS_TABLE']
BILLING_TABLE = os.environ['BILLING_TABLE']
NOTIFICATIONS_TABLE = os.environ['NOTIFICATIONS_TABLE']

# DynamoDB table objects
users_table = dynamodb.Table(USERS_TABLE)
storage_units_table = dynamodb.Table(STORAGE_UNITS_TABLE)
billing_table = dynamodb.Table(BILLING_TABLE)
notifications_table = dynamodb.Table(NOTIFICATIONS_TABLE)

def lambda_handler(event, context):
    # Determine the HTTP method
    http_method = event['httpMethod']

    if http_method == 'GET':
        # GET request - Retrieve users or storage units
        if 'users' in event['path']:
            return get_users(event)
        elif 'units' in event['path']:
            return list_storage_units(event)
        elif 'support/units/status' in event['path']:
            return list_units_by_status(event)

    elif http_method == 'POST':
        # POST request - Create user, book unit, share access
        if 'users' in event['path']:
            return create_user(event)
        elif 'units/book' in event['path']:
            return book_storage_unit(event)
        elif 'units/share' in event['path']:
            return share_storage_access(event)

    elif http_method == 'PUT':
        # PUT request - Manage payment
        if 'payment' in event['path']:
            return manage_payment(event)

    elif http_method == 'DELETE':
        # DELETE request - Cancel booking
        if 'units/cancel' in event['path']:
            return cancel_booking(event)

    return {
        'statusCode': 404,
        'body': json.dumps({'message': 'Resource not found'})
    }

# Helper function to get all users
def get_users(event):
    try:
        response = users_table.scan()
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'])
        }
    except ClientError as e:
        return handle_error(e)

# Helper function to list all storage units
def list_storage_units(event):
    try:
        response = storage_units_table.scan()
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'])
        }
    except ClientError as e:
        return handle_error(e)

# Helper function to list storage units by status (Support Staff)
def list_units_by_status(event):
    status = event['pathParameters']['status']
    try:
        response = storage_units_table.query(
            KeyConditionExpression="status = :status",
            ExpressionAttributeValues={":status": status}
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'])
        }
    except ClientError as e:
        return handle_error(e)

# Helper function to create a new user
def create_user(event):
    try:
        body = json.loads(event['body'])
        user_id = body['userId']
        email = body['email']
        name = body['name']
        new_user = {
            'userId': user_id,
            'email': email,
            'name': name,
            'createdAt': datetime.now().isoformat()
        }
        users_table.put_item(Item=new_user)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'User created successfully'})
        }
    except ClientError as e:
        return handle_error(e)

# Helper function to book a storage unit
def book_storage_unit(event):
    try:
        body = json.loads(event['body'])
        user_id = body['userId']
        facility_id = body['facilityId']
        unit_id = body['unitId']
        booking_date = datetime.now().isoformat()

        # Check if unit is available
        response = storage_units_table.get_item(
            Key={'facilityId': facility_id, 'unitId': unit_id}
        )
        unit = response.get('Item', {})

        if not unit or unit['status'] != 'Available':
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Unit is not available'})
            }

        # Update unit status to Reserved
        storage_units_table.update_item(
            Key={'facilityId': facility_id, 'unitId': unit_id},
            UpdateExpression="SET status = :status, reservedBy = :userId, bookingDate = :bookingDate",
            ExpressionAttributeValues={
                ':status': 'Reserved',
                ':userId': user_id,
                ':bookingDate': booking_date
            }
        )

        # Record the booking in billing table (for payment management)
        billing_table.put_item(Item={
            'userId': user_id,
            'paymentId': f"{user_id}-{unit_id}-{booking_date}",
            'unitId': unit_id,
            'facilityId': facility_id,
            'bookingDate': booking_date,
            'status': 'Pending'
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Unit booked successfully'})
        }
    except ClientError as e:
        return handle_error(e)

# Helper function to share access to a storage unit
def share_storage_access(event):
    try:
        body = json.loads(event['body'])
        user_id = body['userId']
        share_with_user = body['shareWithUser']
        unit_id = body['unitId']
        share_start = body.get('startDate', datetime.now().isoformat())
        share_end = body.get('endDate', share_start)

        # Check if the user owns the unit
        response = storage_units_table.get_item(
            Key={'facilityId': body['facilityId'], 'unitId': unit_id}
        )
        unit = response.get('Item', {})

        if not unit or unit['reservedBy'] != user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'You do not own this unit'})
            }

        # Record the access share in notifications table
        notifications_table.put_item(Item={
            'userId': user_id,
            'notificationId': f"{unit_id}-share-{share_with_user}",
            'shareWithUser': share_with_user,
            'unitId': unit_id,
            'facilityId': body['facilityId'],
            'shareStart': share_start,
            'shareEnd': share_end
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Access shared successfully'})
        }
    except ClientError as e:
        return handle_error(e)

# Helper function to manage payment (e.g., update billing info)
def manage_payment(event):
    try:
        body = json.loads(event['body'])
        user_id = body['userId']
        payment_method = body['paymentMethod']

        # Update payment method in the billing table
        response = billing_table.update_item(
            Key={'userId': user_id, 'paymentId': body['paymentId']},
            UpdateExpression="SET paymentMethod = :paymentMethod",
            ExpressionAttributeValues={':paymentMethod': payment_method}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Payment method updated successfully'})
        }
    except ClientError as e:
        return handle_error(e)

# Helper function to cancel a booking
def cancel_booking(event):
    try:
        booking_id = event['pathParameters']['bookingId']

        # Cancel booking logic here (update status, handle billing, etc.)
        response = billing_table.update_item(
            Key={'paymentId': booking_id},
            UpdateExpression="SET status = :status",
            ExpressionAttributeValues={':status': 'Cancelled'}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Booking cancelled successfully'})
        }
    except ClientError as e:
        return handle_error(e)

# Helper function for error handling
def handle_error(e):
    return {
        'statusCode': 500,
        'body': json.dumps({'message': f"Error: {str(e)}"})
    }
