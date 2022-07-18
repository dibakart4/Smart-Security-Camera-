# Marinos Galiatsatos
# July 28, 2019

from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import time
import smtplib, ssl, sys
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = cv2.VideoCapture(0)

FROM = "dibakar@gmail.com" # enter here the sender's mail
TO = "dibakar@gmail.com" # enter here the receiver's mail
password = "########" # enter here the sender's password

SUBJECT = "Potential Threat!"

while(True):
    # Capture frame-by-frame
	ret, frameorig = cap.read()
 
	frame = imutils.resize(frameorig, width=min(400, frameorig.shape[1]))

	# detect people
	(rects, weights) = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
 
	# apply non-maxima suppression to the bounding boxes using a
	# fairly large overlap threshold to try to maintain overlapping
	# boxes that are still people
	rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
	pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
 
	if rects.size is not 0:
		print("found a person!")
		img_name = "thief{}.png".format(time.time())
		cv2.imwrite(img_name, frame)

		msg = MIMEMultipart()
		msg["To"] = TO
		msg["From"] = FROM
		msg["Subject"] = SUBJECT
		msgText = MIMEText('<b></b><br><img src="cid:%s"><br>' % (img_name), 'html')  
		msg.attach(msgText)

		fp = open(img_name, 'rb')
		img = MIMEImage(fp.read())
		fp.close()
		img.add_header('Content-ID', '<{}>'.format(img_name))
		msg.attach(img)

		try:
			server_ssl = smtplib.SMTP("smtp.gmail.com", 587)
			server_ssl.ehlo() 
			server_ssl.starttls()
			server_ssl.login(FROM, password)
			server_ssl.sendmail(FROM, TO, msg.as_string())
			server_ssl.close()
			print("successfully sent the mail.")
			print("Waiting...")
			cv2.waitKey(30000) # wait for 3 minutes
		except Exception as e:
			print(e)

	# draw the final bounding boxes
	for (xA, yA, xB, yB) in pick:
		cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

    # Display the resulting frame
	cv2.imshow('Security Camera',frame)
	                              #if cv2.waitKey(1) & 0xFF == ord('q'):
	c = cv2.waitKey(1) 
	if c == 27: 
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
