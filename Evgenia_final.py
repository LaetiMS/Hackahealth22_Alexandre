## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
import copy
import os

#Send a text to speech command
os.system("echo \"ciao alexandre\" | festival --tts")  

# Define thresholds and convolution kernel
threshold_data = 3000
threshold_up = 2500
threshold_down = 200
kernel = np.ones((10,10),np.float32)/100

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)


stim = 0
try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        #Cropping the image to avoid a big part of the floor
        depth_image = depth_image[0:100, 100:350]
        color_image = color_image[0:100, 100:350] 
        
        # 
        raw = copy.deepcopy(depth_image)        
        raw_w_threshold = copy.deepcopy(depth_image)
        raw_w_threshold[raw_w_threshold > threshold_data] = 100000                       # Remove all values higher than threshold
    
        # Filter with kernel (low-pass filter)
        raw_filtered = cv2.filter2D(depth_image, -1, kernel)
        raw_filtered_w_threshold = copy.deepcopy(raw_filtered)
        raw_filtered_w_threshold[raw_filtered_w_threshold > threshold_data] = 100000    # Remove all values higher than threshold

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        raw_colormap                            = cv2.applyColorMap(cv2.convertScaleAbs(raw,                            alpha=0.03), cv2.COLORMAP_JET)
        raw_w_threshold_colormap                = cv2.applyColorMap(cv2.convertScaleAbs(raw_w_threshold,                alpha=0.03), cv2.COLORMAP_JET)
        raw_filtered_w_threshold_colormap       = cv2.applyColorMap(cv2.convertScaleAbs(raw_filtered_w_threshold,       alpha=0.03), cv2.COLORMAP_JET)
        
        
        raw_colormap_dim = raw_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if raw_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(raw_colormap_dim[1], raw_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, raw_colormap, raw_filtered_w_threshold_colormap))
        else:
            images = np.hstack((color_image, raw_colormap, raw_filtered_w_threshold_colormap))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        
        cv2.waitKey(1)
        
        # Find points within a window
        indices = np.argwhere( (raw_filtered_w_threshold > threshold_down) & (raw_filtered_w_threshold < threshold_up))
        #indices = np.argwhere( (raw_w_threshold_filtered < threshold_detection) )
        

        # We stimulate if the number of pixels within the value range is above a certain number (worked with 1500, should work with a higher value as well -> around 5000)
        if indices.shape[0] > 1500: 
                os.system("echo \"obstacle\" | festival --tts") 
                print("TTS obstacle", stim)
                stim+=1
                
       

finally:

    # Stop streaming
    pipeline.stop()
