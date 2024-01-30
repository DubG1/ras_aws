# ras_aws
Road analysis system that takes images from roads and calculates parking slot availability and detects traffic jams with aws rekognition and is deployed using aws step functions.

This is the description of our functions:

 - loadImages: Loads every image which is stored in a given S3 bucket and returns a list exisiting of these images

 - identifyImages: Determines if the given image is a "Parking Lot" image or a "Traffic" image. The result is a list of list where the in the   first index the list of "Parking Lot" images are stored and in the second index the list of "Traffic" images


 - In Parallel:
    
    - identifySlots: Detects for each image the free parking slots. The output is an array of detected boxes (slots).

    - filterSlots: For each image all non-valid slots are deleted. A slot is non-valid if it is smaller compared to the other detected slots.

    - countSlots: For each image the final number of valid parking slots is counted. The outpur is a tuple consisting of the image and the number of valid slots.




    - customRoadDetection (ParallelFor - custom label): For each image the road is detected. To do that, boxes are collected. Then the surface area is going to be computed which is important to compute the severity of the traffic jam (if there is one). To compute this area it is important not sum up two boxes which do not overlap. A more detailed description is involved within the script.

    - identifyTrafficJams: Determines if the given image pictures a traffic jam. To determine that, we first look if the preinstalled aws rekognition label "Traffic Jam" is involed. If yes then it is a traffic jam image. But there are some situation where we clearly can say that the image is showing a traffic jam but aws rekognition is not able to recognize it. To recognize is a function named "detectSeverity" is used which determines of severe the traffic is. If it is above the predermined threshold 0.10 then it is counted as a traffic jam image.

    - detectSeverity (ParallelFor): For each traffic jam image the serverity is computed. To do that, we first detect all the vehicles, compute the area and determine the sum of it. This value we divide by the area of the road.

    - splitData: Splits images into high, medium and low traffic


- saveTrafficValues: Saves the results of splitData in database

- saveParkingValues: Saves the result of countSlots in database


Reference to data:
    - traffic images from https://www.pixabay.com/
    - parking lot images from https://www.pixabay.com/, https://www.pexels.com/, https://www.istockphoto.com/
