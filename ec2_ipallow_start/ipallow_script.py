import json
import logging
import boto3

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Extract the ip_address and description from the event payload or query parameters
    try:
        if 'body' in event:
            payload = json.loads(event['body'])
            ip_address = payload['ip_address']
            description = payload.get('description', '')
        elif 'queryStringParameters' in event:
            ip_address = event['queryStringParameters']['ip_address']
            description = event['queryStringParameters'].get('description', '')
        else:
            return {
                'isBase64Encoded': False,
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json' },
                'body': json.dumps({'error': 'Missing ip_address in request'})
            }

        # Log the IP address and description
        logger.info(f'IP address: {ip_address}')
        logger.info(f'Description: {description if description else "None provided"}')

        ec2 = boto3.client('ec2')
        security_group_id = '<your_security_group_id>'

        response = ec2.describe_security_groups(GroupIds=[security_group_id])
        existing_permissions = response['SecurityGroups'][0]['IpPermissions']
        for permission in existing_permissions:
            for range in permission['IpRanges']:
                if ('Description' in range) and (range['Description'] == description):
                    try:
                        remove_permission = [{
                            'IpProtocol': permission['IpProtocol'],
                            'FromPort': permission['FromPort'],
                            'ToPort': permission['ToPort'],
                            'IpRanges': [{'CidrIp': range['CidrIp'], 'Description': description}]
                        }]
                        ec2.revoke_security_group_ingress(GroupId=security_group_id, IpPermissions=remove_permission)
                    except Exception as e:
                        logger.error(f"Error occurred while revoking security group ingress: {str(e)}")
                        return {
                            'isBase64Encoded': False,
                            'statusCode': 500,
                            'headers': { 'Content-Type': 'application/json' },
                            'body': json.dumps({'error': str(e)})
                        }
                    try:
                        add_permission = [{
                            'IpProtocol': permission['IpProtocol'],
                            'FromPort': permission['FromPort'],
                            'ToPort': permission['ToPort'],
                            'IpRanges': [{'CidrIp': f"{ip_address}/32", 'Description': description}]
                        }]
                        ec2.authorize_security_group_ingress(GroupId=security_group_id, IpPermissions=add_permission)
                    except Exception as e:
                        logger.error(f"Error occurred while authorizing security group ingress: {str(e)}")
                        return {
                            'isBase64Encoded': False,
                            'statusCode': 500,
                            'headers': { 'Content-Type': 'application/json' },
                            'body': json.dumps({'error': str(e)})
                        }
                    return {
                        'isBase64Encoded': False,
                        'statusCode': 200,
                        'headers': { 'Content-Type': 'application/json' },
                        'body': json.dumps({'message': f'IP address {ip_address} allowed in existing record with description: {description}'})
                    }
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'error': str(e)})
        }
    new_permission = {
        'IpProtocol': 'tcp',
        'FromPort': 80,
        'ToPort': 80,
        'IpRanges': [{
            'CidrIp': f'{ip_address}/32',
            'Description': description
        }],
    }
    try:
        response = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[new_permission]
        )
    except Exception as e:
        logger.error(f"Error occurred while authorizing security group ingress: {str(e)}")
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'error': str(e)})
        }
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        'body': json.dumps({'message': f'IP address {ip_address} allowed in new record with description: {description}'})
    }
