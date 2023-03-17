#!/usr/bin/env python3 

import rospy 
import numpy as np 
import cv2 
from cv_bridge import CvBridge 
from sensor_msgs.msg import Image 

  

img_received = False 
# define a 720x1280 3-channel image with all pixels equal to zero 
rgb_img = np.zeros((720, 1280, 3), dtype = "uint8") 

  

#Algo to get rid of ugly corners, white space/ hand/ etc
def getRidOfCorners(mono_img): 
	#Numpy Array same size as img/mono
	x = np.zeros((720,1280), dtype = "uint8") 

	#Draw a rectangle, will be put on x 
	#Start at 150,150, end at 850, 600, 
	#Will be white
	#Makes white box to neatly fit ball 
	cv2.rectangle(x, (150, 150),(850,600), 255, -1) 
	#Do the & 
	end_result = cv2.bitwise_and(mono_img, x) 
	return end_result 

	 

  

# get the image message 
def get_image(ros_img): 
	global rgb_img 
	global img_received 
	# convert to opencv image 
	rgb_img = CvBridge().imgmsg_to_cv2(ros_img, "rgb8") 
	# raise flag 
	img_received = True 

  

	 

if __name__ == '__main__': 
	# define the node and subcribers and publishers 
	rospy.init_node('detect_ball', anonymous = True) 
	# define a subscriber to ream images 
	img_sub = rospy.Subscriber("/camera/color/image_raw", Image, get_image)  
	# define a publisher to publish images 
	img_pub = rospy.Publisher('/ball_2D', Image, queue_size = 1) 

	 

	# set the loop frequency 
	rate = rospy.Rate(10) 

 
	while not rospy.is_shutdown(): 
		# make sure we process if the camera has started streaming images 
		if img_received: 
		
			#Make HSV		
			hsv = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2HSV) 
			
			# define the upper and lower ranges 
			lower_yellow_hsv = np.array([25,0,0])
			upper_yellow_hsv = np.array([60,255,255]) 
			# filter the image  
			yellow_mask = cv2.inRange(hsv, lower_yellow_hsv, upper_yellow_hsv) 
			
			#Call function on yellow image for one more round of filtering
			yellow_mask = getRidOfCorners(yellow_mask) 

	
			# convert it to ros msg and publish it 
			img_msg = CvBridge().cv2_to_imgmsg(yellow_mask, encoding="mono8") 
			# publish the image 
			img_pub.publish(img_msg) 

		# pause until the next iteration			 
		rate.sleep() 
