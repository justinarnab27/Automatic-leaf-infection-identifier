import cv2
import numpy as np           
import argparse
import os,sys
import time

def endprogram():
	print "\nProgram terminated!"
	sys.exit()
	
	
def clear():
	os.system('clear')

	
def progressbar():
	# Initial call to print 0% progress
	#printProgressBar(i, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
	l=len(filepath)-1
	
	# Update Progress Bar
	printProgressBar(Fid , l, prefix = 'Progress:', suffix = 'Complete', length = 50)
	
	
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '>'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\n\r' + prefix + '||'+ bar + '||' + percent + '%' + suffix)
    # Print New Line on Complete
    if iteration == total: 
        print()


	
#Reading the directory by parsing the argument 
ap = argparse.ArgumentParser()
ap.add_argument("-i","--input",required=True, help="path to image directory")
args =vars(ap.parse_args())
print "\n*********************\nImage Directory : " + args['input'] + "\n*********************"
filepath = [x for x in os.listdir(args['input']) if x.endswith(".jpg")]

y,Y,yes,n,N,no = 1,1,1,0,0,0
confirm = input('The code will run for complete folder. Do you really want to continue(Y/N)?')
#filename = input('\nEnter the file name you wish to update/create:')

if confirm == 1:
	for Fid in range(len(filepath)):
		print'\nProcessing images...'
		progressbar()
		print '\n For a quick start press (s)'
		time.sleep(0.01)
		clear()
elif confirm == 0:
	print '\nProcess terminated by the user!'
	endprogram()

else:
	print 'Invalid input by the user!' 
	endprogram()
	
for Fid in range(len(filepath)):	
	time.sleep(1)
	clear()
	progressbar()
	print "\nImage: " + str(filepath[Fid])
	img = cv2.imread(filepath[Fid])
	img = cv2.resize(img,(275,183))
	original = img.copy()
	neworiginal = img.copy() 
	cv2.imshow('original',img)
	

	#Calculating number of pixels with shade of white(p) to check if exclusion of these pixels is required or not (if more than a fixed %)
	p = 0 
	for i in range(img.shape[0]):
		for j in range(img.shape[1]):
			B = img[i][j][0]
			G = img[i][j][1]
			R = img[i][j][2]
			if (B > 110 and G > 110 and R > 110):
				p += 1

	#finding the % of pixels in shade of white
	totalpixels = img.shape[0]*img.shape[1]
	per_white = 100 * p/totalpixels

	#print 'percantage of white: ' + str(per_white) + '\n'
	#print 'total: ' + str(totalpixels) + '\n'
	#print 'white: ' + str(p) + '\n'


	#excluding all the pixels with colour close to white if they are more than 10% in the image
	if per_white > 10:
		img[i][j] = [200,200,200]
		#cv2.imshow('color change', img)


	#Guassian blur
	blur1 = cv2.GaussianBlur(img,(3,3),1)


	#mean-shift algo
	newimg = np.zeros((img.shape[0], img.shape[1],3),np.uint8)
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER , 10 ,1.0)

	img = cv2.pyrMeanShiftFiltering(blur1, 20, 30, newimg, 0, criteria)
	cv2.imshow('means shift image',img)


	#Guassian blur
	blur = cv2.GaussianBlur(img,(11,11),1)

	#Canny-edge detection
	canny = cv2.Canny(blur, 160, 290)
	cv2.imshow('canny edge detection', canny)
	
	canny = cv2.cvtColor(canny,cv2.COLOR_GRAY2BGR)
	

	#contour to find leafs
	bordered = cv2.cvtColor(canny,cv2.COLOR_BGR2GRAY)
	_, contours,hierarchy = cv2.findContours(bordered, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	maxC = 0
	for x in range(len(contours)):													
		if len(contours[x]) > maxC:													
			maxC = len(contours[x])
			maxid = x

	perimeter= cv2.arcLength(contours[maxid],True)
	#print perimeter
	Tarea = cv2.contourArea(contours[maxid])
	cv2.drawContours(neworiginal,contours[maxid],-1,(0,0,255))
	cv2.imshow('Contour',neworiginal)
	#cv2.imwrite('Contour complete leaf.jpg',neworiginal)



	#Creating rectangular roi around contour
	height, width, _ = canny.shape
	min_x, min_y = width, height
	max_x = max_y = 0
	#frame = canny.copy()

	# computes the bounding box for the contour, and draws it on the frame,
	for contour, hier in zip(contours, hierarchy):
		(x,y,w,h) = cv2.boundingRect(contours[maxid])
		min_x, max_x = min(x, min_x), max(x+w, max_x)
		min_y, max_y = min(y, min_y), max(y+h, max_y)
		if w > 80 and h > 80:
			#cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)   #we do not draw the rectangle as it interferes with contour later on
			roi = img[y:y+h , x:x+w]
			originalroi = original[y:y+h , x:x+w]

	if (max_x - min_x > 0 and max_y - min_y > 0):
		roi = img[min_y:max_y , min_x:max_x]	
		originalroi = original[min_y:max_y , min_x:max_x]
		#cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)   #we do not draw the rectangle as it interferes with contour

	cv2.imshow('ROI', roi)
	img = roi


	#Changing colour-space
	#imghsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	imghls = cv2.cvtColor(roi, cv2.COLOR_BGR2HLS)
	#cv2.imshow('unfiltered HLS', imghls)
	imghls[np.where((imghls==[30,200,2]).all(axis=2))] = [0,200,0]
	cv2.imshow('HLS', imghls)

	#Only hue channel
	huehls = imghls[:,:,0]
	#cv2.imshow('img_hue hls',huehls)
	#ret, huehls = cv2.threshold(huehls,2,255,cv2.THRESH_BINARY)

	huehls[np.where(huehls==[0])] = [35]
	cv2.imshow('processed_img hue hls',huehls)


	#Thresholding on hue image
	ret, thresh = cv2.threshold(huehls,28,255,cv2.THRESH_BINARY_INV)
	#cv2.imshow('thresh', thresh)


	#Masking thresholded image from original image
	mask = cv2.bitwise_and(originalroi,originalroi,mask = thresh)
	cv2.imshow('masked out img',mask)


	#Finding contours for all infected regions
	_, contours,heirarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	Infarea = 0
	for x in range(len(contours)):
		cv2.drawContours(originalroi,contours[x],-1,(0,0,255))
		cv2.imshow('Contour masked',originalroi)

		#Calculating area of infected region
		Infarea += cv2.contourArea(contours[x])

	if Infarea > Tarea:
		Tarea = roi.shape[0]*roi.shape[1]

	print '___________________________\n| Perimeter: ' + str(perimeter) + ' |\n|_________________________|'
	
	print '_______________________\n| Total area: ' + str(Tarea) + ' |\n|_____________________|'
	
	#Finding the percentage of infection in the leaf
	print '________________________\n| Infected area: ' + str(Infarea) + ' |\n|______________________|'

	per = 100 * Infarea/Tarea

	print '_________________________________________________\n| Percentage of infection region: ' + str(per) + ' |\n|_______________________________________________|'
	
	
	print("\nDo you want to update the dataset file with the above results(Y/N):")
	n = cv2.waitKey(0) & 0xFF
	import csv
	filename = 'datasetleafmixed.csv'
	
	while True:	
		if  n == ord('y'or'Y'):
			print 'Appending to '+ str(filename)+ '...'  
			print("\nIs it infected or not(Y/N)?:")
			detection = cv2.waitKey(0) & 0xFF
			
			if  detection == ord('y'or'Y'):
					labelling = 1
					print("\nIt is set as infected!")
					
			elif detection == ord('n' or 'N') :
					labelling = 0
					print("\nIt is set as healthy!")

					
			else:
				print "Invalid input!"
				break
			
			fieldnames = ['fortnum', 'imgid', 'label', 'feature1', 'feature2', 'feature3']

			#To append in previously created file
			try:
				results = []
				with open(filename) as File:
					reader = csv.DictReader(File)
					for rows in reader:
						results.append(rows)
				try:
					#first character(fortnum) of previously appended line 
					prefort = int(results[len(results)-1]['fortnum'])			
				#if new file  			
				except IndexError:
					prefort = -1

				if prefort < 9:
					fortnum = prefort + 1
				elif prefort > 9:
					fortnum = 0
				file.close(File)
				
				L = {'fortnum': str(fortnum), 'imgid': str(filepath[Fid]), 'label': str(labelling), 'feature1': str(Tarea), 'feature2': str(Infarea), 'feature3': str(perimeter)}
				
				
				with open(filename,'a') as File:

					writer = csv.DictWriter(File, fieldnames = fieldnames)

					writer.writerow(L)

					file.close(File)

			#To write a new file (IOError -> when dataset file not found in directory)
			except IOError:
				fortnum = 0
				L = {'fortnum': str(fortnum), 'imgid': str(filepath[Fid]), 'label': str(labelling), 'feature1': str(Tarea), 'feature2': str(Infarea), 'feature3': str(perimeter)}
				
				with open(filename,'w') as File:

					writer = csv.DictWriter(File, fieldnames = fieldnames)

					writer.writeheader()

					writer.writerow(L)

					file.close(File)

			finally:
				print '\nFile '+ str(filename)+ ' updated!'
				break

			
		elif n == ord('n' or 'N') :
			print '\nFile not updated!'
			break

		elif n == ord('q' or 'Q'):
			endprogram()
			
		else:
			print '\nInvalid input!'
			break
