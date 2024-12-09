import boto3
import os
import json

sns_client = boto3.client('sns')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def send_notification(subject, message, customer_email):
    """
    Send a notification to a customer via AWS SNS.
    """
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps({
                "default": message,
                "email": message
            }),
            Subject=subject,
            MessageStructure='json'
        )
        print(f"Notification sent to {customer_email}: {response}")
        return {"status": "success", "message_id": response['MessageId']}
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return {"status": "error", "error_message": str(e)}

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    """
    try:
        body = json.loads(event['body'])
        subject = body['subject']
        message = body['message']
        customer_email = body['customer_email']

        response = send_notification(subject, message, customer_email)

        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "error_message": str(e)})
        }
