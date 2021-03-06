from picamera import PiCamera
from fractions import Fraction
import picamera.array
import sys
import serial
import io
import time
import numpy as np
import cv2
import math
import random
import RobotAI
import DroneUtils

import socket
import string



ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 0);

def danceMonkeyDance():
        print("wat")
        for i in range(1,30):
                print(i)
                ser.write('m' + random.choice(['l','r']) +str(random.choice(range(0,359))).zfill(4));
               # time.sleep(2)
        

def sendCmd(str):
# To move the robot a specific distance, just include it as the modifer value
# To move the robot 1 foot, send mf0001.
# To move the robot 10 feet, send mf0010.
	#Move Forward
        if str == 'm':
                danceMonkeyDance()
	if str == 'w':
		ser.write('mf0100');
	#Move Backward
	if str == 's':
		ser.write('mb0001');
# For 360 degree turns, send the modifer value 360
# For 180 degree turns, send the modifer value 180
# Degree turns can be 360, 180, 90, 45, and 20 degrees
	#Turn Left
	if str == 'a':
		ser.write('ml0090');
	#Turn Right
	if str == 'd':
	 	ser.write('mr0090');
	#Laser Toggle
	if str == 'f':
		ser.write('l00000');
	#Move Servo Up 5 degrees
	if str == 'i':
		ser.write('su0001');
	#Move Servo Right 5 degrees
	if str == 'l':
		ser.write('sr0090');
	#Move Servo Down 5 degrees
	if str == 'k':
		ser.write('sd0001');
	#Move Servo Left 5 degrees
	if str == 'j':
		ser.write('sl0090');
	#Reset servos
	if str == 'x':
		ser.write('sx0000');
        if str == 'y':
                takePictures()
        #Get lasers distance
	if str == 'r':
		d = getCurDist();
		print d;
	#Get paper distance
	if str == 'b':
		d = getPaperDist();
		print d;
	#Get lasers positon
	if str == 't':
		p = getLaserPos();
		print p;
	#Find boxes
        if str == 'p':
                s = findBox();
		print s;
        if str == 'u':
                ser.write('l00000');
                takePictures()
                ser.write('l00000');
                print("Done")
        if str == 'z':
               	getBoxCorners()
	#Point laser to right most box
	if str == 'e':
		pointToRightBox();
		print "I found the right box!"
	#Point laser to left most box
	if str == 'q':
		pointToLeftBox();
		print "I found the left box!"
        if str == 'v':
                calibrate()
	#Testrun
        if str == '.':
                takeOnePicture()
	if str == 'c':
		automateCalibration();
		print "Done"
	if str == 'g':
		RobotAI.itsAlive()
		print "Dancing.."
	#	danceMonkeyDance()
	#Quit Program
	if str == 'quit':
		ser.close();
		sys.exit(0);	
	else:
                return;

def pointToLeftBox():
	boxes = findBox();
	laser = getLaserPos();
	centerLaser(boxes[0], laser, 0);

def pointToRightBox():
	boxes = findBox();
	laser = getLaserPos();
	centerLaser(boxes[1], laser, 1);

def centerLaser(boxes, laser, direction):
	boxMinX = boxes[0];
	len = boxes[2];
	boxMaxX = (boxMinX + len);
	boxMinY = boxes[1];
	hgt = boxes[3];
	boxMaxY = (boxMinY + hgt);
	laserX = laser[0];
	laserY = laser[1];

	if laserX > boxMaxX :
		ser.write('sl0010');
		if direction == 0 :
			pointToLeftBox();
		if direction == 1 :
			pointToRightBox();
	if laserX < boxMinX :
		ser.write('sr0010');
		if direction == 0 :
			pointToLeftBox();
		if direction == 1 :
			pointToRightBox();
	if laserY > boxMaxY :
		ser.write('su0010');
		if direction == 0 :
			pointToLeftBox();
		if direction == 1 :
			pointToRightBox();
	if laserY < boxMinY :
		ser.write('sd0010');
		if direction == 0 :
			pointToLeftBox();
		if direction == 1 :
			pointToRightBox();
	else:
		return;


def waitForFrames(cam,num):
        for i in range(0,num):
                camera.capture(stream,format='jpeg')
                
##################################################################################
# This method captures and returns two images, taken simultaneously from the same
# position. One image is taken with the laser, the other without.
# Returns an array of data for two images, ready to be written to an image file.
# @return  images[]
#	images[0] = image taken with laser on
#	images[1] = image taken with laser off
def toggleLaserPictures():
	#Setup camera an stuffs
	camera = PiCamera();
        camera.brightness = 30
	camera.resolution = (2592,1944)
        camera.awb_mode='incandescent'
	#time.sleep(2)
	stream = io.BytesIO();	
	#Turn on laser and get first image, captured into a stream
	ser.write('l00000');
	time.sleep(2);
	camera.capture(stream, format='png');
	img1Data = np.fromstring(stream.getvalue(), dtype=np.uint8);	
	stream.close();
	#Turn off laser and get second image, then read image into a new stream
	ser.write('l00000');
	time.sleep(2);
	stream = io.BytesIO();
	camera.capture(stream, format='png');
	img2Data = np.fromstring(stream.getvalue(), dtype=np.uint8);
	stream.close();	
	images = [img1Data, img2Data];
	camera.close();
	return 	images;

#Same as above^
def laserOnOffPictures():
	camera = PiCamera()
	camera.resolution = (2592, 1944)
	stream = io.BytesIO()
	#Laser on, picture time
	ser.write('100000')
	time.sleep(2)
	camera.capture(stream, format='png')
	img1Data = np.fromstring(stream.getvalue(), dtype=np.uint8)
	stream.close();
	#Laser off, picture time
	ser.write('l00000')
	time.sleep(1)
	stream = io.BytesIO()
	camera.capture(stream, format='png')
	img2Data = np.fromstring(stream.getvalue(), dtype=np.uint8)
	stream.close()
	images = [img1Data]
	camera.close()
	return images


def getOnePic():
        print("WATER")
	camera = PiCamera()
	camera.resolution = (2592, 1944)
	stream = io.BytesIO()
	ser.write('l00000')
	time.sleep(2)
	camera.capture(stream, format='png')
        camera.close()
	img1Data = np.fromstring(stream.getvalue(), dtype=np.uint8)
	stream.close();
        ser.write('l00000')
	return img1Data

# DO NOT MESS WITH THIS PLZ
#SRSLY NEED FOR LAZAR
# LIKE SERIOUISLY DONT TOUCH IT EVER
# but........ okay.
def takeOnePicture():
        camera = PiCamera()
        camera.brightness = 30
       # camera.led = False
        camera.awb_mode='incandescent'
        #camera.awb_gains = (Fraction(295,256), Fraction(515, 256))
        camera.resolution = (2592,1944)
        stream = io.BytesIO()
        camera.capture(stream,format='png')
        data = np.fromstring(stream.getvalue(),dtype=np.uint8)
        image = cv2.imdecode(data,1)
        cv2.imwrite("OnePic.png",image);
        print(camera.awb_gains);
        camera.close()
        print("done")


def takePictures():
        camera = PiCamera()
        #
        camera.resolution = (2592,1944)
        stream = io.BytesIO()
        camera.capture(stream,format='png')
        data = np.fromstring(stream.getvalue(),dtype=np.uint8)
        image = cv2.imdecode(data,1)
        cv2.imwrite("img.png",image);
        camera.close()
        
def findBox():
        camera = PiCamera()
        camera.resolution = (2592,1944)
        camera.brightness = 75
        stream= io.BytesIO()
        camera.capture(stream,format='png')
        data = np.fromstring(stream.getvalue(),dtype=np.uint8)
        image = cv2.imdecode(data,1)
        stuff = DroneUtils.getAllBoxes(image.tostring('c'), image.shape[1],image.shape[0])

        for box in stuff:
                cv2.rectangle(image,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(255,255,0),5)
        cv2.imwrite('FindBox.png',image)
        camera.close()
        cv2.destroyAllWindows()
        return stuff;


def getBoxCorners():
        camera = PiCamera();
        camera.resolution = (2592,1944)
        stream = io.BytesIO()
        camera.capture(stream,format='png')
        data = np.fromstring(stream.getvalue(),dtype=np.uint8)
        image = cv2.imdecode(data,1)
        cv2.imshow("Image",image)
        cv2.waitKey(10)
        lst = DroneUtils.getBoxCorner(image.tostring('c'),image.shape[1],image.shape[0])
        for i in lst:
                for x in range(len(i)/2):
                        print(str(i[2*x]) + " " + str(i[2*x+1]))
        cv2.imwrite("output.png",image)
        camera.close()
        cv2.destroyAllWindows()
        print(lst)

##################################################################################
#  This method uses the robots laser to determine how far away the object it is
# pointing at is. 
# @ return  dist -distance in feet
def getCurDist():
	images = toggleLaserPictures();
	img1 = cv2.imdecode(images[0],1);
	#img2 = cv2.imdecode(images[1], 1);
	cv2.imwrite("ta.png", img1);
	#cv2.imwrite("tb.png", img2);
	dist = DroneUtils.getLaserDistOneImg(img1.tostring('c'), img1.shape[1], img1.shape[0],255.405, 922.538);
	return dist;


#################################################################################
#	This method uses the dimensions and ratio of a piece of paper to determine
# its distance by utilizing its contour lines.
# @ return dist -distance in feet
def getPaperDist():
	images = laserOnOffPictures();
	img = cv2.imdecode(images[0], 1);
	#cv2.imwrite("t1a.png", img);
	dist = DroneUtils.getPaperDistContour(img.tostring('c'), img.shape[1], img.shape[0]);
	return dist;


def getPaperDistWithDat(image):
        img = cv2.imdecode(image,1)
        dist = DroneUtils.getPaperDistContour(img.tostring('c'), img.shape[1], img.shape[0]);
	return dist;


##################################################################################
#	This method gets a piece of papers corner points. The first two values in
# the returned list are the top-right corner of the paper. The next two values are
# the top-left corner points, the next two are the bottom-left, and the final two
# are the bottom-right. For each point, the first value is the x-cord and the 2nd
# is the y-cord.
# @ return pointList  -List of points in the image where the papers corners are.
def getPaperPoints():
	images = laserTogglePictures();
	img = cv2.imdecode(images[1], 1);
	cv2.imwrite("crnrs.png",img);
	#pointList = DroneUtils.getPaperByCorner(img.tostring('c'), img.shape[1], img.shape[0]);
	pointList = DroneUtils.paperContour(img.tostring('c'), img.shape[1], img.shape[0]);
	return pointList;


def getLaserPosWithDat(image):
	img1 = cv2.imdecode(image, 1);
        pos = DroneUtils.getLaserDistOneImgLoc(img1.tostring('c'), img1.shape[1], img1.shape[0]);
	return pos;	


##################################################################################
#	This method returns the x,y position of the laser within the image. The
# first value in the list is the laser's x-cord. and the second is the y-cord.
# @ return pos  - Point of the laser
# 	pos[0] - x
#	pos[1] - y
def getLaserPos():
	images = toggleLaserPictures();
	img1 = cv2.imdecode(images[0], 1);
        cv2.imwrite('test.png',img1)
        pos = DroneUtils.getLaserDistOneImgLoc(img1.tostring('c'), img1.shape[1], img1.shape[0]);
	return pos;	


def calibrate():
        print("wat")
        startDist = 10
        ptsLst = []
        img = getOnePic()
        distance= getPaperDistWithDat(img)
        laserPt = getLaserPosWithDat(img)
        apndLst = [distance, laserPt[1]]
        ptsLst.append(apndLst)
        ser.write('mf0001');
        time.sleep(2)
        print("ALL OF MY WAT")
        for i in xrange(3):
                img = getOnePic()
                distance = getPaperDistWithDat(img)
                lasarPt = getLaserPosWithDat(img)
                apnd = [distance, lasarPt[1]]
                ser.write('mf0001')
                ptsLst.append(apnd)
                time.sleep(2)
        print(ptsLst)
        consts = DroneUtils.getLaserConstants(ptsLst)
        print(consts[0])
        print(consts[1])
        
        
        

##################################################################################
#	This method moves the robot in 5 foot increments, taking two images of its
# target object at every 5 feet. One image is with the laser on, and the other w/o
# This method periodically checks to make sure the target object is within its img
# This method is complete once the ro bot has moved within 5 feet of the target.
def automateCalibration():
	#Get intial distance to paper
	distToPaper = getCurDist();
	print ("Current distance is %02d" % distToPaper);
	while (distToPaper > 5):
		#Take images of paper
		print ("Taking imagery... ");
		images = laserOnOffPictures();
		img1 = cv2.imdecode(images[0], 1);
		img2 = cv2.imdecode(images[1], 1);
		cv2.imwrite('%02d_withLaser.png' % distToPaper, img1);
		cv2.imwrite('%02d_withOut.png' % distToPaper, img2);

		#Advance the robot 5 feet
		print ("Advancing robots position..");
		ser.write('mf0005');

		#Get the points of paper
		print ("Getting coordinates of paper... ");
		pts = getPaperPoints();

		#Center laser/camera
		centerLaser(pts);

		#Get new distance to paper
		distToPaper = getCurDist();
		print("Current distance is %02d" % distToPaper);
	return;


##################################################################################
#	This method can be called to ensure that the robots laser and camera are
# pointed somewhere within the given bounds of an image. This method will first 
# get the robots horizontal servo centered, and then the vertical.
def centerLaser(bounds):
	xMax = getMax(bounds[0], bounds[4]); 
	xMin = getMin(bounds[2], bounds[6]);
	yMax = getMax(bounds[5], bounds[7]);
	yMin = getMin(bounds[1], bounds[3]);
	centeredH = False;
	centeredV = False;
	#Center horizontal
	print "Centering camera/laser horizontally... ";
	while not(centeredH):
		lzrPts = getLaserPos();
		lzrX = lzrPts[0];
		lzrY = lzrPts[1];
		#if laser is too far left, move it right
		if (xMax > lzrX and lzrX < xMin):
			ser.write('sr0001');
		#if laser is too far right, move it left
		if (xMax < lzrX and lzrX > xMin):
			ser.write('sl0001');
		else:
			centeredH = True;
	#Center vertical
	print "Centering camera/laser vertically...";
	while not(centeredV):
		lzrPts = getLaserPos();
		lzrX = lzrPts[0];
		lzrY = lzrPts[1];
		#if laser is too high, move it down
		if (yMax > lzrY and lzrY < yMin):
			ser.write('sd0001');
			ser.write('sd0001');
		#if laser is too low, move it up	
		if (yMax < lzrY and lzrY > yMin):
			ser.write('su0001');
			ser.write('su0001');
		else:
			centeredV = True;


##################################################################################
# Helper method to return the max value of two given numbers.
def getMax(a, b):
	if (a > b):
		return a;
	else:
		return b;

##################################################################################
# Helper method to return the min value of two given numbers.
def getMin(a, b):
	if (a<b):
		return a;
	else:
		return b;



##################################################################################
##################################################################################

print "Now controlling the Ground Robot"
print "------------------------------------------------------------"
print "To move teh drone:"
print "  w = forward"
print "  s = backward"
print "  a = left"
print "  d = right"
print " "
print "To toggle the laser: f"
print " "
print "To move the servos:"
print "  j = turn left"
print "  k = look down"
print "  l = turn right"
print "  i = look up"
print "  x = reset servo positions"
print " "
print "To get a distance read:"
print " r = Get distance to laser"
print " b = Get distance alt. "
print " t = Get position of laser"
print " p = Find boxes"
print " q = Point laser to left most box"
print " e = Point laser to right most box"
print " c = calibrate lzr"
print " "
print "------------------------------------------------------------"
print "Type 'quit' to exit the program"



# while 1:
# 	cmd = raw_input("");
# 	if cmd:
# 		sendCmd(cmd);


def parse_socket_request(rawRequest):
	# "Turn basic request headers in something we can use"
	temp = [i.strip() for i in rawRequest.splitlines()]
	
	if -1 == temp[0].find('HTTP'):
		raise InvalidRequest('Incorrect Protocol')
	
	# Figure out our request method, path, and which version of HTTP we're using
	method, path, protocol = [i.strip() for i in temp[0].split()]
	
	# Create the headers, but only if we have a GET reqeust
	headers = {}
	if 'GET' == method:
		for k, v in [i.split(':', 1) for i in temp[1:-1]]:
			headers[k.strip()] = v.strip()
	else:
		raise InvalidRequest('Only accepts GET requests')
	
	return method, path, protocol, headers




HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 8080 # Arbitrary non-privileged port
CLRF = '\r\n' # place holder for return carriage
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
 
#now keep talking with the client
while 1:
	#wait to accept a connection - blocking call
	conn, addr = s.accept()

	rawRequest = conn.recv(1024)

	method, path, protocol, headers = parse_socket_request(rawRequest)

	print 'Request from ' + addr[0] + ':' + str(addr[1]) + ' on ' + protocol + ' to ' + path

	if path == '/':
		conn.send('HTTP/1.1 200 OK' + CLRF)
		conn.send('Content-Type: text/html' + CLRF*2)
		conn.send('<html><head><script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script><script>function sendCMD(x) {    $.ajax({        url: "./" + x,        success: function(result) {            console.log("got response: " + result);        }    });};$(document).ready(function() {    $(window).keypress(function(e) {        var ev = e || window.event;        var key = ev.keyCode || ev.which;        if (key == 119) {            sendCMD(\'w\');        };        if (key == 97) {            sendCMD(\'a\');        }        if (key == 115) {            sendCMD(\'s\');        }        if (key == 100) {            sendCMD(\'d\');        }    });    $("#btn").click(function() {        sendCMD($("#cmd").val());    });});</script></head><body><h1>Welcome Good Sir</h1><p>------------------------------------------------------------<br/>To move teh drone:<br/>  w = forward<br/>  s = backward<br/>  a = left<br/>  d = right<br/><br/>To toggle the laser: f<br/><br/>To move the servos:<br/>  j = turn left<br/>  k = look down<br/>  l = turn right<br/>  i = look up<br/>  x = reset servo positions<br/><br/>To get a distance read:<br/> r = Get distance to laser<br/> b = Get distance alt. <br/> t = Get position of laser<br/> p = Find boxes<br/> q = Point laser to left most box<br/> e = Point laser to right most box<br/> c = calibrate lzr<br/><br/>------------------------------------------------------------<br/>Type quit to exit the program</p><p>Enter your command</p><p><input type="text" id="cmd"></p><p><button type="button" id="btn">Send</button></body></html>')

	else:
		cmd = string.replace(path, '/', '')
		# sendCmd(cmd);
		conn.send('HTTP/1.1 200 OK' + CLRF)
		conn.send('Content-Type: text/html' + CLRF*2)
		conn.send('You sent the command '+cmd)


	conn.close()

s.close()
