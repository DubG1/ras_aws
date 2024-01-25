import json
import redis


def lambda_handler(event, context):
    image = event['validSlots']
    slotCount = len(image)-1
    imageAndSlots = [image[-1], slotCount]

    r = redis.Redis(host='ec2-18-234-121-36.compute-1.amazonaws.com', port=6379, decode_responses=True)
    r.set('imageWithValidSlots', imageAndSlots)

    return {
        'imageWithValidSlots': imageAndSlots
    }