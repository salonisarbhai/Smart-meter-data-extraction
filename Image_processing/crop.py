import json
import numpy as np
import os
import cv2
import matplotlib.image as mpimg

current_dir = os.getcwd()

files = os.listdir(current_dir)

json_files = [y for y in files if '.json' in y]

if not os.path.exists('out'):
    os.makedirs('out')

if not os.path.exists('saved'):
    os.makedirs('saved')
i = 0

if not os.path.exists('cropped'):
    os.makedirs('cropped')

def order_points(pts):
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")

	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]

	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]

	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
 
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
 
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
 
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
	# return the warped image
	return warped

for f in json_files:
    print('trying to read:',f)
    fl = open(f,'r')
    data = json.load(fl)
    image_name = f[:-4]+'png'
    if not os.path.exists(image_name):
        image_name = f[:-4]+'jpg'
    image = cv2.imread(image_name)
    boxes = data["textBBs"]
    for i,item in enumerate(boxes):
        pts = item["poly_points"]
        pts = np.int32(np.asarray(pts))
        cropped_img = four_point_transform(image,pts)
        mpimg.imsave(os.path.join('cropped',f[:-4]+'_'+str(i)+'.jpg'),cropped_img)
        #cv2.polylines(image,[pts],True,(0,0,255))
    #cv2.imshow('window',image)
    #cv2.waitKey(5000)
    if i <= 5:
        cv2.imwrite('saved/'+image_name,image)
    i+=1