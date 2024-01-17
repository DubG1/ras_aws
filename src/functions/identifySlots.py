import boto3
import json

def identify_slots(img_name, bucket_name):
    # Initialize Rekognition client
    rekognition_client = boto3.client('rekognition')
    
    # S3 object details
    s3_object = {'S3Object': {'Bucket': bucket_name, 'Name': img_name}}
    
    # Detect custom labels with model
    response = rekognition_client.detect_custom_labels(
        ProjectVersionArn='arn:aws:rekognition:us-east-1:022778135666:project/aws_pslot/version/aws_pslot.2024-01-16T12.17.29/1705403849659',
        Image=s3_object
    )

    # Check detected labels for slots
    response = rekognition_client.detect_labels(Image=s3_object)
    labels = response.get('Labels', [])

    for label in labels:
        if label['Name'] == 'Parking Slot' and label['Confidence'] > 60:  # Slot detected
            return True

    return False

def lambda_handler(event, context):
    # Extract input from the event
    json_input = json.loads(event['body'])
    
    img_arr = json_input["imageArr"]
    bucket_name = 'roadanalysis1'
    result = []

    for img in img_arr:
        if identify_slots(img, bucket_name):
            result.append(img)

    print(result)
    response = {
        "statusCode": 200,
        "body": json.dumps({"imgWithSlots": result}),
    }
    
    return response