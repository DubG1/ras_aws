import json
import redis


def lambda_handler(event, context):
    images = event['validSlots']
    ec2Instance = images.pop()

    imageAndSlotsArray = []

    for image in images:
        slotCount = len(image)-1
        imageAndSlots = [image[-1], slotCount]
        imageAndSlotsArray.append(imageAndSlots)

    r = redis.Redis(host=ec2Instance, port=6379, db=0, password='two', decode_responses=True)

    imageAndSlotsArray.append(ec2Instance)

    r.set('imageWithValidSlotsArray', json.dumps(imageAndSlotsArray))

    
    return {
        'imageWithValidSlotsArray': imageAndSlotsArray
    }