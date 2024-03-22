from bosdyn import client
from bosdyn.client.image import ImageClient
from bosdyn.client.lease import LeaseClient
from bosdyn.client.auth import AuthClient
from bosdyn.client import util
from PIL import Image
import cv2
import os
import sys
import io
import numpy as np
import time
IP = '192.168.80.3'
USER = 'username'
PASSWORD = 'password
CAMERA = 'frontleft_fisheye_image'
PIXEL_FORMAT = 'RGB_U8'
PIXEL = 'PIXEL_FORMAT_RGB_U8'
DEPTH_CAM = 'frontleft_depth'
from bosdyn.client import image

def main():
    sdk = client.sdk.create_standard_sdk('spot')
    #create the robot object
    robot = sdk.create_robot(IP)
    auth_client = robot.ensure_client(AuthClient.default_service_name)
    token = auth_client.auth(username=USER,password=PASSWORD)
    robot.authenticate_with_token(token=token)
    robot.time_sync.wait_for_sync()
    assert not robot.is_estopped()
    
    robot.logger.info("lease acquired")
    #create a camera object to capture images from
    camera = robot.ensure_client(ImageClient.default_service_name)
    # image.build_image_request(image_source_name=CAMERA,quality_percent=100,pixel_format=PIXEL_FORMAT)
    
    #probably will set a loop here once testsed will also need to recall where to define the pixel format
    image_response = camera.get_image_from_sources(['frontleft_fisheye_image'])
    dtype = np.uint8
    #get image from buffer
    img = np.frombuffer(image_response[0].shot.image.data,dtype=dtype)
    #decode the image
    img = cv2.imdecode(img,-1)
    #rotate the image
    if image_response[0].source.name[0:5] == "front":
        img = cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)
    elif image_response[0].source.name[0:5] == "right":
        img = cv2.rotate(img,cv2.ROTATE_180)
    #dont overwrite existing image
    counter = 0
    while True:
        image_saved_path = os.path.join( image_response[0].source.name + '_{:0>4d}'.format(counter) + '.jpg')
        counter += 1
        #will likely need to fix teh save path
        print(image_saved_path)
        cv2.imwrite(image_saved_path,img)
        print('wrote:' + image_saved_path)
        time.sleep(.5)
        


main()
