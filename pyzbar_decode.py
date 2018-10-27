# -*- coding: utf-8 -*-
"""
Created on 10/24/2018

@author: Chenyu Peng

Usage: python3 pyzbar_decode.py
"""
from imutils.video import VideoStream
from pyzbar import pyzbar
import imutils
import time
import math
import cv2
import numpy as np

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src = 0).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it to
	# have a maximum width of 400 pixels
	frame = vs.read()
	#frame = imutils.resize(frame, width=400)

	# find the barcodes in the frame and decode each of the barcodes
	barcodes = pyzbar.decode(frame)

	# loop over the detected barcodes
	for barcode in barcodes:
		# extract the bounding box location of the barcode and draw
		# the bounding box surrounding the barcode on the image
		(x, y, w, h) = barcode.rect
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

		points = barcode.polygon
		pts_src = np.array([[points[0][0], points[0][1]],[points[1][0], points[1][1]], [points[2][0], points[2][1]], [points[3][0], points[3][1]]])

		if w == max(w, h):
			pts_dst = np.array([[x, y], [x, y + w], [x + w, y + w], [x + w, y]])
		else:
			pts_dst = np.array([[x, y], [x, y + h], [x + h, y + h], [x + h, y]])

		h, status = cv2.findHomography(pts_src, pts_dst)
		# print(h)
		# print('----------------------------------------------')
		k = np.array([[1280, 0, 629], [0, 1280, 372], [0, 0, 1]])
		retval, rotations, translations, normals = cv2.decomposeHomographyMat(h, k)

		# print(rotations)
		# print('---------------------------------------------------')
		for rotation in rotations:
			sy = math.sqrt(rotation[0, 0] * rotation[0, 0] +  rotation[1, 0] * rotation[1, 0])
			singular = sy < 1e-6
			if not singular:
				ang_x = math.atan2(rotation[2, 1] , rotation[2, 2])
				ang_y = math.atan2(-rotation[2, 0], sy)
				ang_z = math.atan2(rotation[1, 0], rotation[0, 0])
			else:
				ang_x = math.atan2(-rotation[1, 2], rotation[1, 1])
				ang_y = math.atan2(-rotation[2, 0], sy)
				ang_z = 0
			euler = np.array([ang_x * 180 / math.pi, ang_y * 180 / math.pi, ang_z * 180 / math.pi])
			print(euler)
		print('----------------------------------------------------')

		# the barcode data is a bytes object so if we want to draw it
		# on our output image we need to convert it to a string first
		barcodeData = barcode.data.decode("utf-8")
		barcodeType = barcode.type

		# draw the barcode data and barcode type on the image
		text = "{} ({})".format(barcodeData, barcodeType)
		cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	# show the output frame
	cv2.imshow("Barcode Scanner", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
