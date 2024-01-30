import boto3
import cv2
import numpy as np
import math
import redis
import json



def lambda_handler(event, context):
    ec2Instance = event[3]
    image = event[0]
    total_area = event[1]

    vehicle_objects = []
    rekognition = boto3.client('rekognition')

    s3 = boto3.client('s3')

    bucket_name = event[2]
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

    # Save the modified image locally
    # cv2.imwrite('C:/Users/Remzi/Desktop/5.Sem/Verteilte Systeme/PS/Project/images/image_with_boxes_new.jpg', image_np)

    r = redis.Redis(host=ec2Instance, port=6379, db=0, password='two', decode_responses=True)
    r.set('detectedSeveretyImage', json.dumps([image, percentage_filled, ec2Instance]))

    return {
        'detectedSeveretyImage': [image, percentage_filled, ec2Instance]
    }

