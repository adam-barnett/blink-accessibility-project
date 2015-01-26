import cv2
import math

"""
rough plan for this system:
main function:
    - check for detection with eye cascade
    - check for detection with face cascade
    if succesful:
        - pass successful cascade to capture function
    else:
        - check for detection with both at a variety of angles
        - if successful then get a rotation amount
        - then pass the successful cascade and rotation amount to capture function
    - return success or failure along with a rotation matrix and possibly the
        successful cascade type

capture function:
    - give user full instructions
    - count the person down to an image with open eyes
    - count them down to an image with closed eyes
    - display both images
    - save both images in the appropriate slots

"""

class InitEyeCapture():
    def __init__():

        
