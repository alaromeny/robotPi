import time
import numpy as np
import cv2


from Utilities.mbedRPC import *


serdev = '/dev/ttyACM0'

mbed = SerialRPC(serdev, 9600)

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

#Set Variables
ROBOT_STOPPING_DISTANCE = 250
ROBOT_DANGER_DISTANCE = 500
ROBOT_VARIABLES_CURRENTSPEED = 0

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
		print("Too Close")
		MOVFUNC_SERVODRIVER_CLEARALLPWM()
		ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PURERED_LOWINTENSITY)
		#MOVFUNC_SERVODRIVER_CHANGESPEED(0)
		#MOVFUNC_SERVODRIVER_GOBACKWARD()
		#time.sleep(1)
		#BEHFUNC_reverseHalfSpeed();
		#justreversed = true;
		image = SENFUNC_CAMERA_CAPTUREIMAGE()
		imageName = "/home/pi/robotPi/CapturedImages/image" + str(stopImageCount) + ".png"
		cv2.imwrite(imageName, image)
		stopImageCount = stopImageCount + 1
		
		
	#Object to the left
	elif SENREAD_SONAR_FLEFT_READING < ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FCENTRE_READING >= ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FRIGHT_READING >= ROBOT_DANGER_DISTANCE:
		print("Maybe to the left")
		ACTFUNC_LEDS_SETDOUBLECOLOUR(SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY, SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY)
		#if(justreversed){
			#BEHFUNC_turn180();
			#justreversed = false;
		#else:
		MOVFUNC_SERVODRIVER_CHANGESPEED(3)
		MOVFUNC_SERVODRIVER_STEERFORWARD_RIGHT()
		
	#Object to the right
	elif SENREAD_SONAR_FLEFT_READING >= ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FCENTRE_READING >= ROBOT_DANGER_DISTANCE and SENREAD_SONAR_FRIGHT_READING < ROBOT_DANGER_DISTANCE:
		print("maybe to the right")
		ACTFUNC_LEDS_SETDOUBLECOLOUR(SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY, SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY)
		#if(justreversed){
			#BEHFUNC_turn180();
			#justreversed = false;
		#else:
		MOVFUNC_SERVODRIVER_CHANGESPEED(3)
		MOVFUNC_SERVODRIVER_STEERFORWARD_LEFT()
		
		
	#If getting close to object
	elif SENREAD_SONAR_FLEFT_READING < ROBOT_DANGER_DISTANCE or SENREAD_SONAR_FCENTRE_READING < ROBOT_DANGER_DISTANCE or SENREAD_SONAR_FRIGHT_READING < ROBOT_DANGER_DISTANCE:
		print("maybe ahead")
		ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PUREBLUE_LOWINTENSITY)
		#if(justreversed){
			#BEHFUNC_turn180();
			#justreversed = false;
		#else:
		MOVFUNC_SERVODRIVER_CHANGESPEED(7)
		MOVFUNC_SERVODRIVER_GOFORWARD()
		
	#If no pbjects detected
	else:
		print("Safe I think")
		ACTFUNC_LEDS_SETBLOCKLEDCOLOUR(SEN_LEDSTRUP_PUREGREEN_LOWINTENSITY)
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




SENFUNC_INITIALISE_CAMERA()
start_time = time.time()
experimentTime = start_time
imageCount = 0
stopImageCount = 0
print("Time at start is: ", start_time)
MOVFUNC_SERVODRIVER_CHANGESPEED(0)
while True:
	#BEHFUNC_stateMachine()
	regularImageCapture()
	MOVFUNC_SERVODRIVER_GOFORWARD()


	
#mbed.ser.close()
