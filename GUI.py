#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  GUI.py
#  
#  Copyright 2017  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from __future__ import print_function
import time
import numpy as np
import cv2
import RPi.GPIO as GPIO

from Tkinter import *
from Utilities.mbedRPC import *



# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] camera sensor warming up...")
vs = VideoStream().start()
time.sleep(2.0)

log = open("/home/pi/robotPi/log.txt", "w")
print("Encoder Readings:", file = log)

serdev = '/dev/ttyACM0'

mbed = SerialRPC(serdev, 9600, 3)

PIN_FLAG_RPCSTATUS = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_FLAG_RPCSTATUS, GPIO.IN)


 ###########################
 #
 #    Global Variables
 #
 ###########################

#Camera Variables

SEN_CAMERA_PORT = 0
SEN_CAMERA_INITIALDISGUARDFRAMES = 30 #Number of frames to throw away while the camera adjusts to light levels
SEN_CAMERA = cv2.VideoCapture(SEN_CAMERA_PORT) #initialises the camera object to the port at SEN_CAMERA_PORT


#Sonar Sensor Readings
global SENREAD_SONAR_FLEFT_READING
global SENREAD_SONAR_FCENTRE_READING
global SENREAD_SONAR_FRIGHT_READING

#SEncoder Sensor Readings
global SENREAD_ENCODERS_FLEFT_READING
global SENREAD_ENCODERS_FRIGHT_READING
global SENREAD_ENCODERS_BRIGHT_READING

#Encoder Values
global SENVAL_ENCODER_MAXCOUNT
global SENVAL_ENCODER_WHEELCOUNT
global SENVAL_ENCODER_METRE
global SENVAL_ENCODER_CENTIMETRE
global SENVAL_ENCODER_MILLIMETRE


#RF COMMS
global COMMREAD_RFMESSAGE_LATESTMESSAGE
global COMMREAD_RFMESSAGE_MESSAGEREADY

#Robot Variables
global ROBOT_VARIABLES_CURRENTSPEED
global ROBOT_STOPPING_DISTANCE
global ROBOT_DANGER_DISTANCE
global ROBOT_VARIABLES_CURRENTSPEED

global SEN_LEDSTRUP_PURERED_LOWINTENSITY
global SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY
global SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY

global SEN_LEDSTRUP_PURERED_HIGHINTENSITY
global SEN_LEDSTRUP_PUREGREEN_HIGHINTENSITY
global SEN_LEDSTRUP_PUREBLUE_HIGHINTENSITY

global SEN_LEDPARTYMODE

#Set Variables
ROBOT_STOPPING_DISTANCE = 250
ROBOT_DANGER_DISTANCE = 500
ROBOT_VARIABLES_CURRENTSPEED = 0

#SENVAL_ENCODER_MAXCOUNT
SENVAL_ENCODER_WHEELCOUNT = 1788
SENVAL_ENCODER_METRE = 4700
SENVAL_ENCODER_CENTIMETRE = 47
SENVAL_ENCODER_MILLIMETRE = 4.7

SEN_LEDSTRUP_PURERED_LOWINTENSITY = ("40","0","0")
SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY = ("0","40","0")
SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY = ("0","0","40")

SEN_LEDSTRUP_PURERED_HIGHINTENSITY = ("255","0","0")
SEN_LEDSTRUP_PUREGREEN_HIGHINTENSITY = ("0","255","0")
SEN_LEDSTRUP_PUREBLUE_HIGHINTENSITY = ("0","0","255")


def SENFUNC_SONAR_getSonarReadings():
	
	global SENREAD_SONAR_FLEFT_READING
	global SENREAD_SONAR_FCENTRE_READING
	global SENREAD_SONAR_FRIGHT_READING
	result = mbed.rpc("getSonar", "run", "")
	split = result.split("#")
	print(result)
	print(split)
	sonarData = split[1]
	SENREAD_SONAR_FLEFT_READING, SENREAD_SONAR_FCENTRE_READING, SENREAD_SONAR_FRIGHT_READING = sonarData.split(",")
	SENREAD_SONAR_FLEFT_READING = int(SENREAD_SONAR_FLEFT_READING)
	SENREAD_SONAR_FCENTRE_READING = int(SENREAD_SONAR_FCENTRE_READING)
	SENREAD_SONAR_FRIGHT_READING = int(SENREAD_SONAR_FRIGHT_READING)


#Initialise Camera
#Caputre and disguard SEN_CAMERA_INITIALDISGUARDFRAMES frames to allow the webcam to adjust to light levels etc...
def SENFUNC_INITIALISE_CAMERA():
	for i in xrange(SEN_CAMERA_INITIALDISGUARDFRAMES):
		temp = SENFUNC_CAMERA_CAPTUREIMAGE()

# Captures a single image from the camera and returns it in PIL format
def SENFUNC_CAMERA_CAPTUREIMAGE():
 # read is the easiest way to get a full image out of a VideoCapture object.
 retval, im = SEN_CAMERA.read()
 return im


def BEHFUNC_DETECTFACES():
	# loop over the frames from the video stream
	while True:
		# grab the frame from the threaded video stream, resize it to
		# have a maximum width of 400 pixels, and convert it to
		# grayscale
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	 
		# detect faces in the grayscale frame
		rects = detector(gray, 0)
		# loop over the face detections
		for rect in rects:
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to a NumPy
			# array
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)
	 
			# loop over the (x, y)-coordinates for the facial landmarks
			# and draw them on the image
			minX = 9999
			maxX = 0
			minY = 9999
			maxY = 0
			for (x, y) in shape:
				if x<minX:
					minX = x
				if y<minY:
					minY = y
				if x>maxX:
					maxX = x
				if y>maxY:
					maxY = y
				# cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)


			deltaX = maxX-minX
			deltaY = maxY-minY
			x = maxX - (deltaX/2)
			y = maxY - (deltaY/2)
			radius = int(deltaY*0.7)


			cv2.circle(frame, (x, y), radius, (0, 255, 0), 3)
		  
		# show the frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
	 
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
	cv2.destroyAllWindows()





#Asks the MBED to return the first message in the queue
def COMMFUNC_RF_getMessage():
	result = mbed.rpc("getRFMessage", "run", "")
	split = result.split("#")
	messageData = split[1]
	if messageData == "NO_MESSAGES_TO_READ":
		COMMREAD_RFMESSAGE_MESSAGEREADY = False
		print("No Message Available")
	else:
		COMMREAD_RFMESSAGE_LATESTMESSAGE = messageData


def MOVFUNC_SERVODRIVER_CHANGESPEED(speed):
	ROBOT_VARIABLES_CURRENTSPEED = speed
	newSpeed = str(speed)
	result = mbed.rpc("changeSpeed", "run", (newSpeed))
	print("Speed changed ", result)
	
	
	
def SENFUNC_ENCODER_INITREADING(encoderCount):
	encoderCountString = str(encoderCount)
	mbed.rpc("startEncoders", "run", (encoderCountString, ""))
	
 

def SENFUNC_ENCODER_GETREADINGS():
	global SENREAD_ENCODERS_FLEFT_READING
	global SENREAD_ENCODERS_FRIGHT_READING
	global SENREAD_ENCODERS_BRIGHT_READING
	result = mbed.rpc("getEncoderReadings", "run", "")
	split = result.split("#")
	encoderData = split[1]
	print(encoderData, file = log)
	#SENREAD_ENCODERS_FLEFT_READING, SENREAD_ENCODERS_FRIGHT_READING, SENREAD_ENCODERS_BRIGHT_READING = encoderData.split(",")
	#SENREAD_ENCODERS_FLEFT_READING = int(SENREAD_ENCODERS_FLEFT_READING)
	#SENREAD_ENCODERS_FRIGHT_READING = int(SENREAD_ENCODERS_FRIGHT_READING)
	#SENREAD_ENCODERS_BRIGHT_READING = int(SENREAD_ENCODERS_BRIGHT_READING)
 

def SENFUNC_ENCODER_STOPREADINGS():
	result = mbed.rpc("stopEncoders", "run", "")
 

def MOVFUNC_SERVODRIVER_TESTEACHMOTOR():
	result = mbed.rpc("testEachMotor", "run", "")
	
def MOVFUNC_SERVODRIVER_GOFORWARD():
	result = mbed.rpc("goForward", "run", "")
	
def MOVFUNC_SERVODRIVER_GOBACKWARD():
	result = mbed.rpc("goBackward", "run", "")

def MOVFUNC_SERVODRIVER_STEERBACKWARD_RIGHT():
	result = mbed.rpc("steerBackwardRight", "run", "")

def MOVFUNC_SERVODRIVER_STEERBACKWARD_LEFT():
	result = mbed.rpc("steerBackwardLeft", "run", "")

def MOVFUNC_SERVODRIVER_STEERFORWARD_RIGHT():
	result = mbed.rpc("steerForwardRight", "run", "")
	
def MOVFUNC_SERVODRIVER_STEERFORWARD_LEFT():
	result = mbed.rpc("steerForwardLeft", "run", "")

def MOVFUNC_SERVODRIVER_STOPALLWHEELS():
	result = mbed.rpc("stopAllWheels", "run", "")
	
def MOVFUNC_SERVODRIVER_CLEARALLPWM():
	result = mbed.rpc("clearPWMDriver", "run", "")

def ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(colour):
	result = mbed.rpc("setLEDBlockColour", "run", colour)


def ACTFUNC_LEDS_SETDOUBLECOLOUR(colourLeft, colourRight):
	doubleColour = colourLeft + colourRight
	result = mbed.rpc("setLEDDoubleColour", "run", doubleColour)

def ACTFUNC_LEDS_TOGGLEPARTMODE():
	result = mbed.rpc("setLEDPartyMode", "run", "")


def BEHFUNC_stateMachine():
	global SENREAD_SONAR_FLEFT_READING
	global SENREAD_SONAR_FCENTRE_READING
	global SENREAD_SONAR_FRIGHT_READING
	global ROBOT_STOPPING_DISTANCE
	global ROBOT_DANGER_DISTANCE
	global SEN_LEDSTRUP_PURERED_LOWINTENSITY
	global SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY
	global SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY
	global SEN_LEDSTRUP_PURERED_HIGHINTENSITY
	global SEN_LEDSTRUP_PUREGREEN_HIGHINTENSITY
	global SEN_LEDSTRUP_PUREBLUE_HIGHINTENSITY
	global stopImageCount
	
	SENFUNC_SONAR_getSonarReadings()
	
	#If too close to object
	if SENREAD_SONAR_FLEFT_READING < ROBOT_STOPPING_DISTANCE or SENREAD_SONAR_FCENTRE_READING < ROBOT_STOPPING_DISTANCE or SENREAD_SONAR_FRIGHT_READING < ROBOT_STOPPING_DISTANCE:
		#print("Too Close")
		MOVFUNC_SERVODRIVER_CLEARALLPWM()
		#ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PURERED_LOWINTENSITY)
		#MOVFUNC_SERVODRIVER_CHANGESPEED(0)
		#MOVFUNC_SERVODRIVER_GOBACKWARD()
		#time.sleep(1)
		#BEHFUNC_reverseHalfSpeed();
		#justreversed = true;
		
		
	#Object to the left
	elif SENREAD_SONAR_FLEFT_READING < ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FCENTRE_READING >= ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FRIGHT_READING >= ROBOT_DANGER_DISTANCE:
		#print("Maybe to the left")
		#ACTFUNC_LEDS_SETDOUBLECOLOUR(SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY, SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY)
		#if(justreversed){
			#BEHFUNC_turn180();
			#justreversed = false;
		#else:
		MOVFUNC_SERVODRIVER_CHANGESPEED(3)
		MOVFUNC_SERVODRIVER_STEERFORWARD_RIGHT()
		
	#Object to the right
	elif SENREAD_SONAR_FLEFT_READING >= ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FCENTRE_READING >= ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FRIGHT_READING < ROBOT_DANGER_DISTANCE:
		#print("maybe to the right")
		#ACTFUNC_LEDS_SETDOUBLECOLOUR(SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY, SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY)
		#if(justreversed){
			#BEHFUNC_turn180();
			#justreversed = false;
		#else:
		MOVFUNC_SERVODRIVER_CHANGESPEED(3)
		MOVFUNC_SERVODRIVER_STEERFORWARD_LEFT()
		
		
	#If getting close to object
	elif SENREAD_SONAR_FLEFT_READING < ROBOT_DANGER_DISTANCE or SENREAD_SONAR_FCENTRE_READING < ROBOT_DANGER_DISTANCE or SENREAD_SONAR_FRIGHT_READING < ROBOT_DANGER_DISTANCE:
		#print("maybe ahead")
		#ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY)
		#if(justreversed){
			#BEHFUNC_turn180();
			#justreversed = false;
		#else:
		MOVFUNC_SERVODRIVER_CHANGESPEED(7)
		MOVFUNC_SERVODRIVER_GOFORWARD()
		
	#If no pbjects detected
	else:
		#print("Safe I think")
		#ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY)
		MOVFUNC_SERVODRIVER_CHANGESPEED(0)
		MOVFUNC_SERVODRIVER_GOFORWARD()

def regularImageCapture():
	global start_time
	global imageCount
	elapsed_time = time.time() - start_time
	if elapsed_time > 1:
		image = SENFUNC_CAMERA_CAPTUREIMAGE()
		imageName = "/home/pi/robotPi/CapturedImages/experiment2_image"  + str(imageCount) + ".png"
		cv2.imwrite(imageName, image)
		imageCount = imageCount + 1
		print(elapsed_time)
		start_time = time.time()

def CaptureImage(imageName):
		image = SENFUNC_CAMERA_CAPTUREIMAGE()
		imageName = "/home/pi/robotPi/CapturedImages/capturedImage_"  + imageName + ".png"
		print(imageName)
		cv2.imwrite(imageName, image)

def BUTFUNC_FAST():
	MOVFUNC_SERVODRIVER_CHANGESPEED(0)
def BUTFUNC_MEDIUM():
	MOVFUNC_SERVODRIVER_CHANGESPEED(3)
def BUTFUNC_SLOW():
	MOVFUNC_SERVODRIVER_CHANGESPEED(5)
def BUTFUNC_CRAWL():
	MOVFUNC_SERVODRIVER_CHANGESPEED(7)

def BUTFUNC_REDLEDS():
	ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PURERED_LOWINTENSITY)
def BUTFUNC_BLUELEDS():
	ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY)
def BUTFUNC_GREENLEDS():
	ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY)

count = 0

def counting():
	global count
	count = count+1
	print(count)

SENFUNC_INITIALISE_CAMERA()

Label(text="", width=30, height=4).grid(row=0,column=0)

Label(text="Move", width=15, height=4).grid(row=1,column=1)
Button(text='Forward', width=10, command=MOVFUNC_SERVODRIVER_GOFORWARD, height=4).grid(row=2,column=1)
Button(text='Backward', width=10, command=MOVFUNC_SERVODRIVER_GOBACKWARD, height=4).grid(row=3,column=1)
Button(text='STOP', width=10, command=MOVFUNC_SERVODRIVER_STOPALLWHEELS, height=4).grid(row=5,column=1)


Label(text="", width=15, height=4).grid(row=5,column=2)

Label(text="Change Speed", width=15, height=4).grid(row=1,column=3)
Button(text='Fast', width=10, command=BUTFUNC_FAST, height=4).grid(row=2,column=3)
Button(text='Medium', width=10, command=BUTFUNC_MEDIUM, height=4).grid(row=3,column=3)
Button(text='Slow', width=10, command=BUTFUNC_SLOW, height=4).grid(row=4,column=3)
Button(text='Crawl', width=10, command=BUTFUNC_CRAWL, height=4).grid(row=5,column=3)


Label(text="", width=15, height=4).grid(row=6,column=4)

Label(text="Change Colour", width=15, height=4).grid(row=1,column=5)
Button(text='Red', width=10, command=BUTFUNC_REDLEDS, height=4).grid(row=2,column=5)
Button(text='Green', width=10, command=BUTFUNC_GREENLEDS, height=4).grid(row=3,column=5)
Button(text='Blue', width=10, command=BUTFUNC_BLUELEDS, height=4).grid(row=4,column=5)
Button(text='Party Mode', width=10, command=ACTFUNC_LEDS_TOGGLEPARTMODE, height=4).grid(row=5,column=5)

Label(text="", width=15, height=4).grid(row=6,column=6)

Label(text="Vision", width=15, height=4).grid(row=1,column=7)
Button(text='Find Faces', width=10, command=BEHFUNC_DETECTFACES, height=4).grid(row=2,column=7)

Label(text="", width=15, height=4).grid(row=6,column=8)


mainloop()
	
mbed.ser.close()
print("Serial Closed")
