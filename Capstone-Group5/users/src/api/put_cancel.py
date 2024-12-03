import boto3
import json

dynamodb = boto3.resource('dynamodb')
bookings_table = dynamodb.Table('Bookings')
units_table = dynamodb.Table('StorageUnits')

def lambda_handler(event, context):
    try:
        request = json.loads(event['body'])
        booking_id = request['booking_id']

        # Get booking details
        booking = bookings_table.get_item(Key={'booking_id': booking_id})['Item']
        unit_id = booking['unit_id']

        # Delete booking
        bookings_table.delete_item(Key={'booking_id': booking_id})

        # Mark unit as available
        units_table.update_item(
            Key={'unit_id': unit_id},
            UpdateExpression="SET availability = :a",
            ExpressionAttributeValues={":a": "available"}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Booking canceled successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
