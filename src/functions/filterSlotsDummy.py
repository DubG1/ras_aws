def cloud_function(json_input):
    images_with_slots = json_input["imgWithSlots"]
    width_of_car = json_input["width"]
    
    print("executing filterSlots")
    # Processing
    result = "filtered_image"
    # return the result
    res = {
        "filteredImage": result
    }
    return res
