import boto3

def count_slots(img_name, bucket_name):
    #init rekognition
    rekognition_client = boto3.client('rekognition')
    s3_object = {'S3Object': {'Bucket': bucket_name, 'Name': img_name}}
    
    #detect custom labels with model
    response = rekognition_client.detect_custom_labels(
        ProjectVersionArn='version_arn',
        Image=s3_object
    )

    #check detected labels for slots
    slot_count = 0
    labels = response.get('Labels', [])

    for label in labels:
        if label['Name'] == 'Parking Slot' and label['Confidence'] > 80: #slot detected
            slot_count += 1

    return slot_count

def handleImages(json_input):
    imgArr = json_input["imageArr"]
    bucket_name = 'roadanalysis1'
    result = {}
    
    for img in imgArr:
        slot_count = count_slots(img, bucket_name)
        car_count = imgArr[img]
        result[img] = slot_count - car_count

    res = {
        "slotCountDict": result
    }
    return res
