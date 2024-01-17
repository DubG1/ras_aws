import boto3
import json

def is_within_boundary(box, width_boundary, length_boundary):
    # Check if the box width and height are within the specified boundaries
    return 0 <= box['Width'] <= width_boundary and 0 <= box['Height'] <= length_boundary

def count_slots(img_name, bucket_name, width_boundary, length_boundary):
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
    slot_count = 0
    labels = response.get('Labels', [])

    for label in labels:
        if label['Name'] == 'Parking Slot' and label['Confidence'] > 60:  # Slot detected
            if is_within_boundary(label['Geometry']['BoundingBox'], width_boundary, length_boundary):
                slot_count += 1

    return slot_count

def lambda_handler(event, context):
    # Extract input from the event
    json_input = json.loads(event['body'])
    
    img_arr = json_input["imageArr"]
    bucket_name = 'roadanalysis1'
    result = {}

    for img in img_arr:
        slot_count = count_slots(img, bucket_name,  width_boundary=0.5, length_boundary=0.5) # set car dimensions
        result[img] = slot_count


    response = {
        "statusCode": 200,
        "body": json.dumps({"slotCountDict": result}),
    }
    
    return response
