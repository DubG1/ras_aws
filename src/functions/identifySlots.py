import boto3

def identifySlots(img_name, bucket_name):
    #init rekognition
    rekognition_client = boto3.client('rekognition')
    s3_object = {'S3Object': {'Bucket': bucket_name, 'Name': img_name}}
    
    #detect custom labels with model
    response = rekognition_client.detect_custom_labels(
        ProjectVersionArn='version_arn',
        Image=s3_object
    )

    #check detected labels for slots
    response = rekognition_client.detect_labels(Image=s3_object)
    labels = response.get('Labels', [])

    for label in labels:
        if label['Name'] == 'Parking Slot' and label['Confidence'] > 80:  #slot detected
            return True

    return False

def handleImages(json_input):
    imgArr = json_input["imageArr"]
    bucket_name = 'roadanalysis1'
    result = []
    
    for img in imgArr:
        if identifySlots(img, bucket_name):
            result.append(img)

    res = {
        "imgWithSlots": result
    }
    return res
