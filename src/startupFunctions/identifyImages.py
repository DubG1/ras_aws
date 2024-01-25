import json
import boto3
import redis


def lambda_handler(event, context):
    imgArr = event['images']
    bucket_name = event['bucketName']
    identified_parking_lot_images = []
    identified_traffic_jam_images = []
    
    rekognition = boto3.client('rekognition')
    
    for img in imgArr:
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': img
                }
            }
        )
    
        

        # Check if 'Traffic Jam' label is present
        is_traffic_jam = any(label['Name'] == 'Road' for label in response['Labels'])
        
        # Check if 'Parking' label is present
        is_parking_area = any(label['Name'] == 'Parking Lot' for label in response['Labels'])
        
        if is_parking_area:
            identified_parking_lot_images.append([img, event['parkingProjectArn'], event['parkingModelArn'], event['parkingVersionName'], event['bucketName']])
        elif is_traffic_jam:
            identified_traffic_jam_images.append([img, event['trafficProjectArn'], event['trafficModelArn'], event['trafficVersionName'], event['bucketName']])

    
    r = redis.Redis(host='', port=6379, decode_responses=True)
    r.set('identifiedImages', json.dumps([identified_parking_lot_images, identified_traffic_jam_images]))
    
    
    return {
        'identifiedImages': [identified_parking_lot_images, identified_traffic_jam_images]
    }
