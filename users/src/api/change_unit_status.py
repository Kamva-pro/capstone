import os
import boto3
from http import HTTPStatus

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('STORAGE_UNITS_TABLE')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Changes the status of a specific storage unit.
    Expects a JSON body with 'unit_id' and 'new_status'.
    """
    try:
        # Parse request body
        body = event.get('body', {})
        if isinstance(body, str):
            import json
            body = json.loads(body)

        unit_id = body.get('unit_id')
        new_status = body.get('new_status')

        if not unit_id or not new_status:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "body": "Request must include 'unit_id' and 'new_status'."
            }

        # Update the unit's status in DynamoDB
        response = table.update_item(
            Key={'unit_id': unit_id},
            UpdateExpression="SET #status = :new_status",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':new_status': new_status},
            ReturnValues="UPDATED_NEW"
        )

        return {
            "statusCode": HTTPStatus.OK,
            "body": f"Unit {unit_id} status updated to {new_status}."
        }

    except Exception as e:
        print(f"Error changing unit status: {e}")
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": "An error occurred while processing the request."
        }
