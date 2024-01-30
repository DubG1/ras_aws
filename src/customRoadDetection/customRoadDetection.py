#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import json
import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import time
import redis

detected_boxes = []
total_area = 0

def lambda_handler(event, context):
    ec2Instance = event[0]
    image = event[1]
    project_arn=event[2]
    model_arn=event[3]
    min_inference_units=1 
    version_name=event[4]
    bucket_name=event[5]

    # startingModel(project_arn, model_arn, min_inference_units, version_name)

    analyzeImage(image, model_arn, bucket_name)

    calculateAreas()

    # stopModel(model_arn)

    r = redis.Redis(host=ec2Instance, port=6379, db=0, password='two', decode_responses=True)

    r.set('roadWithArea', json.dumps([image, total_area, bucket_name, ec2Instance]))

    return {
        'roadWithArea': [image, total_area, bucket_name, ec2Instance]
    }




# detected boxes will consist of tuples in this form: [x, y, width, height, wasUsedInComputation]


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
    
def startingModel(project_arn, model_arn, min_inference_units, version_name):
    project_arn=project_arn
    model_arn=model_arn
    min_inference_units=min_inference_units
    version_name=version_name
    start_model(project_arn, model_arn, version_name, min_inference_units)


def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    # draw = ImageDraw.Draw(image)

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

            detected_boxes.append([left, top, width, height, False])
           
       
            # fnt = ImageFont.truetype('C:/Users/Remzi/Desktop/5.Sem/Verteilte Systeme/PS/Project/Fonts/Arial.ttf', 50)
            # fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)

            
            # draw.text((left,top), customLabel['Name'], fill='#00d400', font=fnt)

            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Label Width: ' + "{0:.0f}".format(width))
            print('Label Height: ' + "{0:.0f}".format(height))

            # points = (
            #     (left,top),
            #     (left + width, top),
            #     (left + width, top + height),
            #     (left , top + height),
            #     (left, top))
            # draw.line(points, fill='#00d400', width=5)

    # image.show()
    # image.save('C:/Users/Remzi/Desktop/5.Sem/Verteilte Systeme/PS/Project/images/newImage.jpg')

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    display_image(bucket,photo,response)

    return len(response['CustomLabels'])

def analyzeImage(img, model, bucket_name):
    bucket=bucket_name
    photo=img
    model=model
    min_confidence=60

    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    print("Custom labels detected: " + str(label_count))



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



# We first check for each box if it is fullInBox.
# fullInBox is true if the Box is fully enclosed in another box. Then we don't need to calculate the area for that box
    
def topLeftVertexInBox(box1Tuple, box2Tuple):
    if box1Tuple[1] >= box2Tuple[1] and box1Tuple[0] >= box2Tuple[0] and box1Tuple[0] <= (box2Tuple[0] + box2Tuple[2]) and box1Tuple[1] <= (box2Tuple[1] + box2Tuple[3]):
        return True
    
    return False

def topRightVertexInBox(box1Tuple, box2Tuple):
    if (box1Tuple[0] + box1Tuple[2]) > box2Tuple[0] and (box1Tuple[0] + box1Tuple[2]) <= (box2Tuple[0] + box2Tuple[2]) and box1Tuple[1] < (box2Tuple[1] + box2Tuple[3]) and box1Tuple[1] >= box2Tuple[1]:
        return True
    
    return False

def bottomLeftVertexInBox(box1Tuple, box2Tuple):
    if box1Tuple[0] >= box2Tuple[0] and box1Tuple[0] <= (box2Tuple[0] + box2Tuple[2]) and (box1Tuple[1] + box1Tuple[3]) <= (box2Tuple[1] + box2Tuple[3]) and (box1Tuple[1] + box1Tuple[3]) >= box2Tuple[1]:
        return True
    
    return False

def bottomRightVertexInBox(box1Tuple, box2Tuple):
    if (box1Tuple[0] + box1Tuple[2]) >= box2Tuple[0] and (box1Tuple[0] + box1Tuple[2]) <= (box2Tuple[0] + box2Tuple[2]) and (box1Tuple[1] + box1Tuple[3]) <= (box2Tuple[1] + box2Tuple[3]):
        return True
    
    return False


def fullInBox(box1Tuple, box2Tuple):
    if topLeftVertexInBox(box1Tuple, box2Tuple) and topRightVertexInBox(box1Tuple, box2Tuple) and bottomLeftVertexInBox(box1Tuple, box2Tuple) and bottomRightVertexInBox(box1Tuple, box2Tuple):
        return True
    
    return False


def toBeDeleted(boxTuple, copy_detected_boxes):
    for i in copy_detected_boxes:
        if fullInBox(boxTuple, i):
            return True
    return False


# if all fullInBoxes are deleted from the list 'detected_boxes', if look if the given box in the list
# is just inBox in another box. 'inBox' means that just a part of it's area is involed in another box

# to be inBox at least one vertex has to be in the other box
def inBox(box1Tuple, box2Tuple):
    if topLeftVertexInBox(box1Tuple, box2Tuple) or topRightVertexInBox(box1Tuple, box2Tuple) or bottomLeftVertexInBox(box1Tuple, box2Tuple) or bottomRightVertexInBox(box1Tuple, box2Tuple):
        return True
    
    return False


# first look for to be deleted boxes
def deleteFullInBox():
    for i in detected_boxes:
        copy_detected_boxes = detected_boxes.copy()
        copy_detected_boxes.remove(i)
        if toBeDeleted(i, copy_detected_boxes):
            print("To be deleted is:")
            print(i)
            detected_boxes.remove(i)



def computeArea(box1Tuple, box2Tuple, wl, hl):
    global total_area
    print("I am in computeArea")
    area1 = box2Tuple[2] * box2Tuple[3]
    area2 = wl * hl
    if box1Tuple[4] is True and box2Tuple[4] is False:
        area1 -= area2
        total_area += area1
        box2Tuple[4] = True
        print("computing 1. if")

    elif box2Tuple[4] is True and box1Tuple[4] is False:
        area = box1Tuple[2] * box1Tuple[3]
        area -= area2
        total_area += area
        box1Tuple[4] = True
        print("computing 2. elif")

    elif box2Tuple[4] is False and box1Tuple[4] is False:
        area1 = box2Tuple[2] * box2Tuple[3]
        area2 = wl * hl
        print("area2")
        print(area2)
        area3 = box1Tuple[2] * box1Tuple[3]
        area3 -= area2
        total_area += (area1 + area3)
        box1Tuple[4] = True
        box2Tuple[4] = True
        print("computing else")
    

def checkParts(box1Tuple, box2Tuple):
    if topLeftVertexInBox(box2Tuple, box1Tuple):
        wl = abs((box1Tuple[0] + box1Tuple[2]) - box2Tuple[0])
        hl = abs((box1Tuple[1] + box1Tuple[3]) - abs(box2Tuple[1] - box1Tuple[1]))
        print("topLeft")
        computeArea(box1Tuple, box2Tuple, wl, hl)
    
    elif topRightVertexInBox(box2Tuple, box1Tuple):
        wl = abs(box1Tuple[0] - (box2Tuple[0] + box2Tuple[2]))
        hl = abs((box1Tuple[1] + box1Tuple[3]) - box2Tuple[1])
        print("topRight")
        computeArea(box1Tuple, box2Tuple, wl, hl)
    
    elif bottomRightVertexInBox(box2Tuple, box1Tuple):
        wl = abs(box1Tuple[0] - (box2Tuple[1] + box2Tuple[3]))
        hl = abs(box1Tuple[1] - (box2Tuple[1] + box2Tuple[3]))
        print("bottomRight")
        computeArea(box1Tuple, box2Tuple, wl, hl)
    
    elif bottomLeftVertexInBox(box2Tuple, box1Tuple):
        wl = abs((box1Tuple[0] + box1Tuple[2]) - box2Tuple[0])
        hl = abs(box1Tuple[1] - (box2Tuple[1] + box2Tuple[3]))
        print("bottomLeft")
        computeArea(box1Tuple, box2Tuple, wl, hl)
        
    
    elif box1Tuple[0] >= box2Tuple[0] and (box1Tuple[0] + box1Tuple[2]) <= (box2Tuple[0] + box2Tuple[2]) and (box1Tuple[1] + box1Tuple[3]) > (box2Tuple[1] + box2Tuple[3]):
        wl = abs(box1Tuple[0] - (box2Tuple[0] + box2Tuple[2]))
        hl = abs(box1Tuple[1] - (box2Tuple[1] + box2Tuple[3]))
        print("6.)")
        computeArea(box1Tuple, box2Tuple, wl, hl)

    elif box1Tuple[0] >= box2Tuple[0] and (box1Tuple[0] + box1Tuple[2]) <= (box2Tuple[0] + box2Tuple[2]):
        wl = box1Tuple[2]
        hl = abs(box1Tuple[3] - (abs(box2Tuple[1] - (box1Tuple[1] + box1Tuple[3]))))
        print("2.)")
        computeArea(box1Tuple, box2Tuple, wl, hl)
    
    elif box1Tuple[0] < (box2Tuple[0] + box2Tuple[2]) and (box1Tuple[0] + box1Tuple[2]) > (box2Tuple[0] + box2Tuple[2]):
        wl = abs((box1Tuple[0] + box1Tuple[2]) - (box2Tuple[0] + box2Tuple[2]))
        hl = box1Tuple[3]
        print("4.)")
        computeArea(box1Tuple, box2Tuple, wl, hl)
    
    else:
        wl = abs(box2Tuple[0] - (box1Tuple[0] + box1Tuple[2]))
        hl = box1Tuple[3]
        print("8.)")
        computeArea(box1Tuple, box2Tuple, wl, hl)



def calculateArea(boxTuple, copy_detected_boxes):
    global total_area
    for i in copy_detected_boxes:
        if inBox(i, boxTuple):
            checkParts(i, boxTuple)
        
        elif inBox(boxTuple, i):
            checkParts(boxTuple, i)
        
        else:
            print("I am in else calulcateArea")
            area1 = boxTuple[2] * boxTuple[3]
            area2 = i[2] * i[3]

            if boxTuple[4] is False and i[4] is False:
                total_area += (area1+area2)
                boxTuple[4] = True
                i[4] = True
                print("1.if")

            elif boxTuple[4] is False and i[4] is True:
                total_area += area1
                boxTuple[4] = True
                print("2.elif")

            elif boxTuple[4] is True and i[4] is False:
                total_area += area2
                i[4] = True
                print("3.elif")
        

def calculateAreas():
    global total_area
    deleteFullInBox()
    if len(detected_boxes) == 1:
        area1 = detected_boxes[0][2] * detected_boxes[0][3]
        total_area += area1
        return
    
    for i in detected_boxes:
        copy_detected_boxes = detected_boxes.copy()
        copy_detected_boxes.remove(i)
        print("i am in calculateAreas")
        calculateArea(i, copy_detected_boxes)


# startingModel()
# analyzeImage()
# print("Detected Boxes")
# print(detected_boxes)

# print("After delete")
# print(detected_boxes)

# calculateAreas()
# print("Total area")
# print(total_area)

# detectSeverity('medium2.jpg', total_area)
# stopModel()

# myJson = {
#     "img": 'high1.jpg'
# }

# print(lambda_handler(myJson, ' '))