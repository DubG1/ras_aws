import json
import boto3
import redis

def lambda_handler(event, context):
    # TODO implement
    bucket_name = event['bucketName']
    s3 = boto3.client('s3')
    
    response = s3.list_objects(Bucket=bucket_name)
    
    image_filenames = [obj['Key'] for obj in response.get('Contents', [])]

    r = redis.Redis(host=event['ec2Instance'], port=6379, db=0, password='two', decode_responses=True)

    r.set('images', json.dumps(image_filenames))
    
    return {
        'images': image_filenames,
        'ec2Instance': event['ec2Instance'],
        'trafficProjectArn': event['trafficProjectArn'],
        'trafficModelArn': event['trafficModelArn'],
        'trafficVersionName': event['trafficVersionName'],
        'parkingProjectArn': event['parkingProjectArn'],
        'parkingModelArn': event['parkingModelArn'],
        'parkingVersionName': event['parkingVersionName'],
        'bucketName': event['bucketName']
    }