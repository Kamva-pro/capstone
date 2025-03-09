import json
import boto3
import os
import json
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError


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

# Main Lambda handler updated to route these new endpoints
def lambda_handler(event, context):
    try:
        http_method = event['httpMethod']
        path = event['path']

        if http_method == 'GET':
            if '/users' in path:
                return get_users()
            elif '/units' in path:
                return list_storage_units()
            elif '/support/units/status' in path:
                return list_units_by_status(event)
        elif http_method == 'POST':
            if '/users' in path:
                return create_user(event)
            elif '/units/book' in path:
                return book_storage_unit(event)
            elif '/units/share' in path:
                return share_access(event)
        elif http_method == 'PUT':
            if '/payment' in path:
                return manage_payment(event)
            elif '/support/units/status' in path:
                return update_unit_status(event)
        elif http_method == 'DELETE':
            if '/units/cancel' in path:
                return cancel_booking(event)

        return response(404, {'message': 'Resource not found'})
    except Exception as e:
        return response(500, {'message': 'Internal server error', 'error': str(e)})

def get_users():
    try:
        result = users_table.scan()
        return response(200, result['Items'])
    except ClientError as e:
        return handle_error(e)

def list_storage_units():
    try:
        result = storage_units_table.scan()
        return response(200, result['Items'])
    except ClientError as e:
        return handle_error(e)

def create_user(event):
    body = json.loads(event['body'])
    user = {
        'userid': body['userid'],
        'name': body['name'],
        'createdAt': datetime.utcnow().isoformat()
    }
    users_table.put_item(Item=user)
    return response(201, {'message': 'User created successfully'})

def book_storage_unit(event):
    body = json.loads(event['body'])
    facility_id = body['facilityId']
    unit_id = body['unitId']
    user_id = body['userId']

    try:
        unit = storage_units_table.get_item(Key={'facilityId': facility_id, 'unitId': unit_id}).get('Item')
        if not unit or unit['status'] != 'Available':
            return response(400, {'message': 'Unit not available'})

        storage_units_table.update_item(
            Key={'facilityId': facility_id, 'unitId': unit_id},
            UpdateExpression="SET #status = :status, reservedBy = :userId",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'Reserved', ':userId': user_id}
        )

        return response(200, {'message': 'Unit booked successfully'})
    except ClientError as e:
        return handle_error(e)

def cancel_booking(event):
    booking_id = event['pathParameters']['bookingId']
    # Add logic to cancel the booking
    return response(200, {'message': f'Booking {booking_id} cancelled successfully'})

# New helper function to manage payment
def manage_payment(event):
    try:
        body = json.loads(event['body'])
        user_id = body['userId']
        payment_method = body['paymentMethod']

        billing_table.update_item(
            Key={'userId': user_id, 'paymentId': body['paymentId']},
            UpdateExpression="SET paymentMethod = :paymentMethod",
            ExpressionAttributeValues={':paymentMethod': payment_method}
        )

        return response(200, {'message': 'Payment method updated successfully'})
    except ClientError as e:
        return handle_error(e)

# New helper function to share access to a unit
def share_access(event):
    try:
        body = json.loads(event['body'])
        facility_id = body['facilityId']
        unit_id = body['unitId']
        shared_with = body['sharedWith']

        storage_units_table.update_item(
            Key={'facilityId': facility_id, 'unitId': unit_id},
            UpdateExpression="SET sharedWith = list_append(if_not_exists(sharedWith, :empty_list), :sharedWith)",
            ExpressionAttributeValues={':sharedWith': [shared_with], ':empty_list': []}
        )

        return response(200, {'message': 'Access shared successfully'})
    except ClientError as e:
        return handle_error(e)

def list_units_by_status(event):
    try:
        # Extract the status from the URL path parameters
        status = event['pathParameters']['status']
        print(f"Filtering by status: {status}")

        # Use the filter expression with Attr
        result = storage_units_table.scan(
            FilterExpression=Attr('status').eq(status),
        )

        # Log the result for debugging
        print(f"Filtered units: {result['Items']}")

        # Return the filtered items
        return response(200, result['Items'])

    except ClientError as e:
        # Handle the error (add logging if needed)
        print(f"Error querying DynamoDB: {e}")
        return handle_error(e)

# New helper function to update the status of a unit
def update_unit_status(event):
    try:
        body = json.loads(event['body'])
        facility_id = body['facilityId']
        unit_id = body['unitId']
        new_status = body['status']

        storage_units_table.update_item(
            Key={'facilityId': facility_id, 'unitId': unit_id},
            UpdateExpression="SET status = :status",
            ExpressionAttributeValues={':status': new_status}
        )

        return response(200, {'message': 'Unit status updated successfully'})
    except ClientError as e:
        return handle_error(e)

def handle_error(error):
    return response(500, {'message': error.response['Error']['Message']})

def response(status, body):
    return {
        'statusCode': status,
        'body': json.dumps(body),
        'headers': {'Content-Type': 'application/json'}
    }
