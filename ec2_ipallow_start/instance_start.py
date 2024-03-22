import boto3
import json

def lambda_handler(event, context):
    ec2_resource = boto3.resource('ec2')

    instance_id = '<your_instance_id>'
    instance = ec2_resource.Instance(instance_id)

    try:
        instance.start()
        return {
            'statusCode': 200,
            'body': json.dumps('Instance started')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error occurred: {str(e)}')
        }
