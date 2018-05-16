from tkinter import *
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog
import numpy as np
import cv2
import object_segmentation as seg
import threading


def update_img_callback(val):
	'''
	Update the thresholded image based on the trackbar values. Catch
	value errors if min values > max values (reset the min. trackbars
	in this case).
	'''

	global max_hue, max_saturation, max_value
	global min_hue, min_saturation, min_value
	global lower_range, upper_range
	#global panelRGB, panelBinary, panelThresh
	#global img_bgr, img_hsv, img_rgb

	#readjust trackbar values if min values > max values.
	if max_hue.get() < min_hue.get():
		min_hue.set(max_hue.get())
	if max_saturation.get() < min_saturation.get():
		min_saturation.set(max_saturation.get())
	if max_value.get() < min_value.get():
		min_value.set(max_value.get())
	
	
	min_h = min_hue.get()
	min_s = min_saturation.get()
	min_v = min_value.get()

	max_h = max_hue.get()
	max_s = max_saturation.get()
	max_v = max_value.get()

	#define range for dice in HSV
	lower_range = np.array([min_h, min_s, min_v])
	upper_range = np.array([max_h, max_s, max_v])

def video_feed_thread():

	global lower_range, upper_range, cap
	global panelRGB, panelBinary, panelThresh
	global img_bgr, single_image_mode, new_image
	#Select camera to use for video capture
	cap = cv2.VideoCapture(0)

	#resize video to be 240x320
	cap.set(3, 320)
	cap.set(4, 240)
	while True:
		if single_image_mode is False:	
			ret, img_bgr = cap.read()
		elif (single_image_mode is True) and (new_image is True):
			img_path = filedialog.askopenfilename()
			if len(img_path) > 0:
				img_bgr = cv2.imread(img_path, cv2.IMREAD_COLOR)
				new_image = False
			
		#Convert image color scales
		img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
		img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
		

		img_binarized, img_thresh = seg.binarize_image(img_bgr, img_hsv, lower_range, upper_range)

		#convert the images to PIL format
		img_rgb_PIL = Image.fromarray(img_rgb)
		img_binarized_PIL = Image.fromarray(img_binarized)
		img_thresh_PIL = Image.fromarray(img_thresh)

		#convert then to ImageTK format to be displayed in tkinter GUI
		img_rgb_tk = ImageTk.PhotoImage(img_rgb_PIL)
		img_binarized_tk = ImageTk.PhotoImage(img_binarized_PIL)
		img_thresh_tk = ImageTk.PhotoImage(img_thresh_PIL)
		
		#Display images in GUI
		panelRGB.configure(image=img_rgb_tk)
		panelBinary.configure(image=img_binarized_tk)
		panelThresh.configure(image=img_thresh_tk)
		panelRGB.image = img_rgb_tk
		panelBinary.image = img_binarized_tk
		panelThresh.image = img_thresh_tk
	cap.release()
def save_threshold_values():
	global save_file_path
	global max_hue, max_saturation, max_value
	global min_hue, min_saturation, min_value

	#open a text file to save values if one has not been choosen
	if save_file_path is None:
		#choose a csv file
		save_file_path = filedialog.askopenfilename()

	if save_file_path.endswith(".txt") or save_file_path.endswith("text"):
		f = open(save_file_path, 'a')	#append data to end of file
		data_str = "%d, %d, %d, %d, %d, %d\n" % (max_hue.get(), max_saturation.get(), max_value.get(), min_hue.get(), min_saturation.get(), min_value.get())
		print(data_str)

		#write data to end of file
		f.write(data_str)
		f.close()
	else:
		print("Invalid File Choosen! Please choose a file ending in .txt or .text")

#Global Variables
cap = None
panelRGB = None
panelBinary = None
panelThresh = None
img_bgr = None
img_hsv = None
img_rgb = None
save_file_path = None
lower_range = np.array([0, 0, 0])
upper_range = np.array([179, 255, 255])
new_image = False

#Video thead
vid_thread = threading.Thread(target=video_feed_thread)
vid_thread.daemon = True
root = Tk()
# create a button, then when pressed, will trigger a file chooser
# dialog and allow the user to select an input image; then add the
# button the GUI

single_image_mode = False
def select_single_image_mode():
	
	global single_image_mode, new_image
	single_image_mode = True
	new_image = True
select_image_btn = Button(root, text="Select an image", command=select_single_image_mode)
select_image_btn.grid(row=0, column=0)

def select_video_mode():
	global single_image_mode, new_image
	single_image_mode = False
	new_image = False
select_video_btn = Button(root, text="Play video", command=select_video_mode)
select_video_btn.grid(row=0, column=1)

save_hsv_vals_btn = Button(root, text="Save Threshold Values", command=save_threshold_values)
save_hsv_vals_btn.grid(row=3, column=2)

#Image Panels
img_bgr = np.zeros((240, 320), dtype=np.int8)
img_bgr = Image.fromarray(img_bgr)
img_bgr = ImageTk.PhotoImage(img_bgr)

panelRGB = Label(root, image=img_bgr)
panelRGB.image = img_bgr
panelRGB.grid(row=0, column=2)

panelBinary = Label(root, image=img_bgr)
panelBinary.image = img_bgr
panelBinary.grid(row=1, column=2)

panelThresh = Label(root, image=img_bgr)
panelThresh.image = img_bgr
panelThresh.grid(row=0, column=3)

#track bars for hsv range selection
#Max Hue
max_hue = Scale(root, to=179, label="Max Hue", orient=HORIZONTAL, command=update_img_callback)
max_hue.grid(row=1, column=0)
max_hue.set(179)

#Max Saturation
max_saturation = Scale(root, to=255, label="Max Sat.", orient=HORIZONTAL, command=update_img_callback)
max_saturation.grid(row=2, column=0)
max_saturation.set(255)

#Max Value
max_value = Scale(root, to=255, label="Max Val.", orient=HORIZONTAL, command=update_img_callback)
max_value.grid(row=3, column=0)
max_value.set(255)

#Min Hue
min_hue = Scale(root, to=179, label="Min Hue", orient=HORIZONTAL, command=update_img_callback)
min_hue.grid(row=1, column=1)
min_hue.set(0)

#Min Saturation
min_saturation = Scale(root, to=255, label="Min Sat.", orient=HORIZONTAL, command=update_img_callback)
min_saturation.grid(row=2, column=1)
min_saturation.set(0)

#Min Value
min_value = Scale(root, to=255, label="Min Val.", orient=HORIZONTAL, command=update_img_callback)
min_value.grid(row=3, column=1)
min_value.set(0)

def kill_gui():
	global cap
	if cap is not None:
		cap.release()
	root.destroy()

root.protocol("WM_DELETE_WINDOW", kill_gui)
vid_thread.start()
root.mainloop()
