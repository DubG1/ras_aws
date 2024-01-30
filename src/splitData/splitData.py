# map traffic jam images in 'Low', 'Medium' and 'High'
# the output should the a dictionary with those three keys and the associated traffic jam images

import json
import redis

def lambda_handler(event, context):

    low = []
    medium = []
    high = []
    
    low_threshold = 0.15
    medium_threshold = 0.45
    
    
    
    for t in event['detectedSeveretyImages']:
        if t['detectedSeveretyImage'][1] <= low_threshold:
            low.append(t['detectedSeveretyImage'][0])
        elif t['detectedSeveretyImage'][1] <= medium_threshold:
            medium.append(t['detectedSeveretyImage'][0])
        else:
            high.append(t['detectedSeveretyImage'][0])
        
    
    image_dict = {"High": high, "Medium": medium, "Low": low}

    ec2Instance = event['detectedSeveretyImages'][0]['detectedSeveretyImage'][2]

    r = redis.Redis(host=ec2Instance, port=6379, db=0, password='two', decode_responses=True)
    
    r.set('splitImages', json.dumps(image_dict))

    
    return {
        'splitImages': image_dict,
        'ec2Instance': ec2Instance
    }