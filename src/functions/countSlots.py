import boto3
import json

def is_within_boundary(box, width_boundary, length_boundary):
    margin = (width_boundary + length_boundary) / 2 * 0.3 # Margin of error for box width and height
    # Check if the box width and height are within the specified boundaries
    return (width_boundary - margin) <= box['Width'] <= (width_boundary + margin) and (length_boundary - margin) <= box['Height'] <= (length_boundary + margin)

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

def get_boundaries(img_name):
    parts = img_name.split('.')[0].split('_')   # split filename by . to remove extension, then split by _ to get width and length
    if len(parts) == 2:
        width = float(parts[0])
        length = float(parts[1])
    return width, length

def lambda_handler(event, context):
    # Extract input from the event
    json_input = json.loads(event['body'])
    
    img_arr = json_input["imageArr"]
    bucket_name = 'roadanalysis1'
    result = {}

    for img in img_arr:
        width_boundary, length_boundary = get_boundaries(img)
        slot_count = count_slots(img, bucket_name,  width_boundary, length_boundary) # set slot dimensions
        result[img] = slot_count


    response = {
        "statusCode": 200,
        "body": json.dumps({"slotCountDict": result}),
    }
    
    return response
