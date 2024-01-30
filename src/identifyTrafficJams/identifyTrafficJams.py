# if the AWS Rekognition detected "Traffic Jam" then everything is ok
# but there can be images where there is still traffic jam on it and AWS Rekognition does not detect it
# then we could invoke the "detectSeverity" function to specify the severity of traffic for a given image to then tell whether it is representig a traffic jam or not
# in this function we identify the road

import boto3
import cv2
import numpy as np
import math
import json
import redis


def lambda_handler(event, context):
    images = event['roadsWithArea']
    traffic_jam_images = []

    rekognition = boto3.client('rekognition')

    for img in images:
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': img['roadWithArea'][2],
                    'Name': img['roadWithArea'][0]
                }
            }
        )

        # Check if 'Traffic Jam' label is present
        is_traffic_jam = any(label['Name'] == 'Traffic Jam' for label in response['Labels'])

        if is_traffic_jam or detectSeverity(img['roadWithArea'][0], img['roadWithArea'][1], img['roadWithArea'][2]) > 0.10:
            traffic_jam_images.append([img['roadWithArea'][0], img['roadWithArea'][1], img['roadWithArea'][2], img['roadWithArea'][3]])
            continue

    r = redis.Redis(host=img['roadWithArea'][3], port=6379, db=0, password='two', decode_responses=True)

    r.set('trafficJamImages', json.dumps(traffic_jam_images))

    return {
        'trafficJamImages': traffic_jam_images
    }



def detectSeverity(image, total_area, bucket_name):
    vehicle_objects = []
    rekognition = boto3.client('rekognition')

    s3 = boto3.client('s3')

    bucket_name = bucket_name
    image_key = image

    response = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_bytes = response['Body'].read()


    # Decode image using OpenCV
    image_np = cv2.imdecode(np.array(bytearray(image_bytes), dtype=np.uint8), cv2.IMREAD_COLOR)
    height, width, _ = image_np.shape

    # Detect objects using AWS Rekognition
    response = rekognition.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=100,
        MinConfidence=5
    )

    # Filter out car labels
    car_labels = [label['Name'] for label in response['Labels'] if label['Name'].lower() == 'car']


    # Draw bounding boxes around detected cars
    for label in car_labels:
        for instance in response['Labels']:
            print(instance)
            print("The name is " + instance['Name'])
            if instance['Name'] == 'Car' or instance['Name'] == 'Bus':
                print("is is a fucking car")
                for box in instance['Instances']:
                    box = box['BoundingBox']
                    print(box)
                    x, y, w, h = int(box['Left'] * width), int(box['Top'] * height), int(box['Width'] * width), int(box['Height'] * height)
                    print("This is x")
                    cv2.rectangle(image_np, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    # Draw point at the center
                    # center_x, center_y = x + w / 2, y + h / 2
                    # cv2.circle(image_np, (x + w // 2, y + h // 2), 14, (0, 0, 255), -1)
                    # vehicle_objects.append((center_x, center_y))

                    print("This is the height:")
                    print(h)
                    print("This is the width:")
                    print(w)
                    vehicle_objects.append(h*w)

            print("\n\n\n\n\n\n")
            


    print(vehicle_objects)
    filled_space = sum(vehicle_objects)
    print("Filled space:")
    print(filled_space)
    percentage_filled = filled_space / total_area
    print("Percentage filled: ")
    print(percentage_filled)

    return percentage_filled





# myJson = {
#     "roadsWithArea": [['high1.jpg', 200000], ['medium1.jpg', 70000], ['high2.jpg', 300000], ['low1.jpg', 2]]
# }

# print(lambda_handler(myJson, ' '))
