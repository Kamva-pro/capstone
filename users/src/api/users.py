# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ['USERS_TABLE'])

def lambda_handler(event, context):
    """
    Main handler for Users-related operations.
    """
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')

    if http_method == 'GET' and path == '/users':
        return get_all_users()
    elif http_method == 'GET' and '/users/' in path:
        user_id = path.split('/')[-1]
        return get_user(user_id)
    elif http_method == 'POST' and path == '/users':
        return create_user(event)
    elif http_method == 'PUT' and '/users/' in path:
        user_id = path.split('/')[-1]
        return update_user(user_id, event)
    elif http_method == 'DELETE' and '/users/' in path:
        user_id = path.split('/')[-1]
        return delete_user(user_id)
    else:
        return respond(400, {'message': 'Invalid operation'})

def get_all_users():
    """Fetch all users."""
    try:
        response = users_table.scan()
        return respond(200, {'users': response.get('Items', [])})
    except ClientError as e:
        return respond(500, {'error': str(e)})

def get_user(user_id):
    """Fetch a single user by ID."""
    try:
        response = users_table.get_item(Key={'userid': user_id})
        if 'Item' in response:
            return respond(200, response['Item'])
        else:
            return respond(404, {'message': 'User not found'})
    except ClientError as e:
        return respond(500, {'error': str(e)})

def create_user(event):
    """Create a new user."""
    try:
        user_data = json.loads(event['body'])
        required_fields = ['userid', 'name', 'email']
        if not all(field in user_data for field in required_fields):
            return respond(400, {'message': 'Missing required fields'})

        users_table.put_item(Item=user_data)
        return respond(201, {'message': 'User created successfully', 'user': user_data})
    except ClientError as e:
        return respond(500, {'error': str(e)})

def update_user(user_id, event):
    """Update an existing user."""
    try:
        user_data = json.loads(event['body'])
        update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in user_data.keys()])
        expression_values = {f":{k}": v for k, v in user_data.items()}

        users_table.update_item(
            Key={'userid': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        return respond(200, {'message': 'User updated successfully'})
    except ClientError as e:
        return respond(500, {'error': str(e)})

def delete_user(user_id):
    """Delete a user."""
    try:
        users_table.delete_item(Key={'userid': user_id})
        return respond(200, {'message': 'User deleted successfully'})
    except ClientError as e:
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

