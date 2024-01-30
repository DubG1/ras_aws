
Identify Slots 
- starts our Rekognition Model and calls a function that detects all custom labels in the image which is only Parking Slot in this case and returns them as a list

Filter Slots
- calculates a margin for how big the box can be for the Parking Slot so we can drop invalid entries out of our list because they can clearly not be a parking slot if they are not within the margin and then returns the list of valid slots

Count Slots
- simply takes the length of the list – 1 because the last entry of the list is the image name itself to know which image the number of slots belong to because we have everything in parallel

And finally we have an array with subarrays that look like this [slotCount, imageName]
