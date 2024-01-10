#### parking slots functions

In identifySlots we loop trhough all images that include a parking lot and see if there are any parkingslots in the image and put the image into the result array.
identify_slots:
    - Takes an image name and bucket name as input
    - Uses Rekognition to detect custom labels (parking slots) in the image
    - Returns a boolean indicating whether parking slots are present in the image

In filterSlots we count how many cars are detected and add it to the result dict with the image and its number of cars (maybe rename it to count cars)
count_cars:
    - Takes an image name and bucket name as input
    - Uses Rekognition to detect labels (cars) in the image
    - Returns the count of detected cars in the image

In countSlots we count the amount of slots and substract it the number of cars in the iamge to get the number of available slots and the result dict has the image name and number of available slots
count_slots:
    - Takes an image name and bucket name as input
    - Uses Rekognition to detect custom labels (parking slots) in the image
    - Returns the count of detected parking slots in the image