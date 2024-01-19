def lambda_handler(event, context):
    image = event['validSlots']
    slotCount = len(image)-1
    imageAndSlots = [image[-1], slotCount]
    return {
        'imageWithValidSlots': imageAndSlots
    }