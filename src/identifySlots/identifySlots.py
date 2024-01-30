import boto3
import io
import time
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import redis
import json

''' Note
my aws acc is deactivated because i exceeded the spending limit so i will have to train a new model as soon as i have a new acc
this code is based on the old model so it doesnt work anymore but it will basically stay the same except the model and project arn's
'''

detected_boxes = []

def lambda_handler(event, context):
    image = event[0]
    project_arn=event[1]
    model_arn=event[2]
    min_inference_units=1 
    version_name=event[3]
    bucket_name=event[4]

    startingModel(project_arn, model_arn, min_inference_units, version_name)

    analyzeImage(image, model_arn, bucket_name)

    stopModel(model_arn)

    detected_boxes.append(image)

    r = redis.Redis(host='ec2-18-234-121-36.compute-1.amazonaws.com', port=6379, decode_responses=True)
    r.set('parkingSlots', json.dumps(detected_boxes))
    

    return {
        'parkingSlots': detected_boxes
    }

def start_model(project_arn, model_arn, version_name, min_inference_units):

    client=boto3.client('rekognition')

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response=client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        #Get the running status
        describe_response=client.describe_project_versions(ProjectArn=project_arn,
            VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage']) 
    except Exception as e:
        print(e)
        
    print('Done...')
    
def startingModel():
    project_arn='arn:aws:rekognition:us-east-1:022778135666:project/aws_pslot/1705403384779'
    model_arn='arn:aws:rekognition:us-east-1:022778135666:project/aws_pslot/version/aws_pslot.2024-01-16T12.17.29/1705403849659'
    min_inference_units=1 
    version_name='aws_pslot.2024-01-16T12.17.29'
    start_model(project_arn, model_arn, version_name, min_inference_units)

#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)


def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']
            detected_boxes.append([left, top, width, height])

            fnt = ImageFont.truetype('C:/Users/georg/OneDrive/Dokumente/Studium_Windows/dist_sys/project/ras_aws/docs/Arial.ttf', 50)
            draw.text((left,top), customLabel['Name'], fill='#00d400', font=fnt)

            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Label Width: ' + "{0:.0f}".format(width))
            print('Label Height: ' + "{0:.0f}".format(height))

            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill='#00d400', width=5)

    image.show()

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    display_image(bucket,photo,response)

    return len(response['CustomLabels'])

def analyzeImage(image, model_arn, bucket_name):

    bucket=bucket_name
    photo=image
    model=model_arn
    min_confidence=20

    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    print("Custom labels detected: " + str(label_count))

#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)



def stop_model(model_arn):

    client=boto3.client('rekognition')

    print('Stopping model:' + model_arn)

    #Stop the model
    try:
        response=client.stop_project_version(ProjectVersionArn=model_arn)
        status=response['Status']
        print ('Status: ' + status)
    except Exception as e:  
        print(e)  

    print('Done...')
    
def stopModel(model_arn):
    
    model_arn=model_arn
    stop_model(model_arn)