import json
import redis

def lambda_handler(event, context):
    values = event['imageAndSlotsArray']
    ec2Instance = values.pop()

    r = redis.Redis(host=ec2Instance, port=6379, db=0, password='two', decode_responses=True)

    for value in values:
        r.set(value[0], value[1])

    imageAndSlotsArray = []

    for value in values:
        imageAndSlotsArray.append([value[0], r.get(value[0])])


    return {
        'imageAndSlotsArray': imageAndSlotsArray
    }