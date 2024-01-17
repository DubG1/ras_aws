import boto3

def count_cars(img_name, bucket_name):
    #init rekognition
    rekognition_client = boto3.client('rekognition')
    s3_object = {'S3Object': {'Bucket': bucket_name, 'Name': img_name}}
    
    #detect labels
    response = rekognition_client.detect_labels(Image=s3_object)

    #count how often car was the label
    car_count = 0
    labels = response.get('Labels', [])

    for label in labels:
        if label['Name'] == 'Car' and label['Confidence'] > 80: #car detected
            car_count += 1

    return car_count

def lambda_handler(json_input):
    imgArr = json_input["imageArr"]
    bucket_name = 'roadanalysis1'
    result = {}
    
    for img in imgArr:
        car_count = count_cars(img, bucket_name)
        result[img] = car_count

    res = {
        "carCountDict": result
    }
    return res
