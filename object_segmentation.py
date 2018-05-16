import cv2
import numpy as np

def binarize_image(img_bgr, img_hsv, hsv_low_range, hsv_high_range):

	#Bound image values to the hsv ranges selected
	mask = cv2.inRange(img_hsv, hsv_low_range, hsv_high_range)
	img_thresh = cv2.bitwise_and(img_bgr, img_bgr, mask=mask)
	img_thresh_gray = cv2.cvtColor(img_thresh, cv2.COLOR_BGR2GRAY)
	#Binarize image using Otsu's Binarization
	threshold, img_binarized = cv2.threshold(img_thresh_gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	img_thresh = cv2.cvtColor(img_thresh, cv2.COLOR_BGR2RGB)
	return img_binarized, img_thresh