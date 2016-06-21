import boto3
from botocore.exceptions import ClientError

def get_queue(queue_name, aws_access_key_id, aws_secret_key, region_name):
    sqs = boto3.resource('sqs',
                        region_name=region_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_accesS_key=aws_secret_access_key
                        )
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        return queue
    except ClientError:
        print('The requested queue does not exist.')


        