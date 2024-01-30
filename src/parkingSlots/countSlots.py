import json
import redis


def lambda_handler(event, context):
    image = event['validSlots']
    slotCount = len(image)-1
    imageAndSlots = [image[-1], slotCount]

    r = redis.Redis(host='', port=6379, decode_responses=True)
    r.set('imageWithValidSlots', imageAndSlots)

    return {
        'imageWithValidSlots': imageAndSlots
    }