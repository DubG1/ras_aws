import boto3
import json
import redis

def is_within_boundary(box, width_boundary, length_boundary):
    margin = (width_boundary + length_boundary) / 2 * 0.3 # Margin of error for box width and height
    # Check if the box width and height are within the specified boundaries
    return (width_boundary - margin) <= box[2] <= (width_boundary + margin) and (length_boundary - margin) <= box[3] <= (length_boundary + margin)

def get_boundaries(image):
    parts = image.split('.')[0].split('_')   # split filename by . to remove extension, then split by _ to get width and length
    if len(parts) == 2:
        width = float(parts[0])
        length = float(parts[1])
    return width, length

def lambda_handler(event, context):
    images = event['parkingSlots']
    ec2Instance = images.pop()

    for image in images:
        if isinstance(image, str):
            continue        
        image_name = image.pop()
        width_boundary, length_boundary = get_boundaries(image_name)

        for box in image:
            if not is_within_boundary(box, width_boundary, length_boundary):
                image.remove(box)
        image.append(image_name)

    r = redis.Redis(host=ec2Instance, port=6379, db=0, password='two', decode_responses=True)
    r.set('validSlots', json.dumps(images))

    images.append(ec2Instance)

    return {
        'validSlots': images
    }