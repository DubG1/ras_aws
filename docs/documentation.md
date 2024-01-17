#### parking slots functions

In identifySlots we loop trhough all images that include a parking lot and see if there are any parkingslots in the image and put the image into the result array.
identify_slots:
    - Gets image array from input
    - Uses Rekognition to detect custom labels (parking slots) in the image
    - Function returns a boolean indicating whether parking slots are present in the image or not
    - Return json object is a lsit of images that have parking slots


In countSlots we count the amount of slots under some conditions available slots and return it with the name of the file in a dictionary.
count_slots:
    - Takes an image name
    - Gets boundaries from the filename
    - Uses Rekognition to detect custom labels (parking slots) in the image
    - Calculates a margin and checks if the slot dimensions are within the boundaries
    - Function returns the count of valid parking slots in the image
    - Return json object is a dictionary with an image and a number that indicates the parkingslots


#### deprecated
In filterSlots we count how many cars are detected and add it to the result dict with the image and its number of cars (maybe rename it to count cars)
count_cars:
    - Takes an image name and bucket name as input
    - Uses Rekognition to detect labels (cars) in the image
    - Returns the count of detected cars in the image