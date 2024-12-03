import os
import boto3
from boto3.dynamodb.conditions import Attr
from http import HTTPStatus

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('STORAGE_UNITS_TABLE')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Lists all storage units by their status.
    Query parameter 'status' is required.
    """
    try:
        # Get status from query parameters
        query_params = event.get('queryStringParameters', {})
        status = query_params.get('status')

        if not status:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "body": "Missing required query parameter: 'status'."
            }

        # Query DynamoDB for storage units with the specified status
        response = table.scan(
            FilterExpression=Attr('status').eq(status)
        )

        units = response.get('Items', [])
        return {
            "statusCode": HTTPStatus.OK,
            "body": units
        }

    except Exception as e:
        print(f"Error listing units by status: {e}")
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": "An error occurred while processing the request."
        }
