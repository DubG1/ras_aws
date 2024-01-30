import json
import redis

def lambda_handler(event, context):

    splitImages = event[1]['splitImages']
    ec2Instance = event[1]['ec2Instance']

    r = redis.Redis(host=ec2Instance, port=6379, db=0, password='two', decode_responses=True)


    r.set('High', json.dumps(splitImages['High']))
    r.set('Medium', json.dumps(splitImages['Medium']))
    r.set('Low', json.dumps(splitImages['Low']))

    highTraffic = [json.loads(r.get('High'))]
    mediumTraffic = [json.loads(r.get('Medium'))]
    lowTraffic = [json.loads(r.get('Low'))]

    imageAndSlotsArray = event[0]['imageWithValidSlotsArray']

    r.set('imageAndSlotsArray', json.dumps(imageAndSlotsArray))

    
    return {
        'highTraffic': highTraffic,
        'mediumTraffic': mediumTraffic,
        'lowTraffic': lowTraffic,
        'imageAndSlotsArray': imageAndSlotsArray
    }

