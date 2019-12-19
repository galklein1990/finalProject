"""
This module handels all stitching, matching and homography calculations in ctr program.
"""




#cv and math imports
import numpy as np
from matplotlib import pyplot as plt
import cv2

#metadata, locations
import PIL.ExifTags
import PIL.Image
from math import radians, cos, sin, asin, sqrt,atan2,degrees,atan
import time
import os
import re
import sys

#programs imports
import in_out as io
import constants as const
from classes import Point,Image,Route,Target
#################################################
#Panorama constants
#################################################
NUM_OF_MATCHES = 50 #matches of descriptors between 2 images
DIRECTION_ACCURACY = 5 #accuracy of course directions in degrees
STITCHING_SERIES = 2 #num of images to stitch at once
#homography matrix sanity
HOMOGRAPHY_DIAGONAL = (0.95,1.05)
MAX_NUMERATOR_COEF = 0.01
MAX_DENUM_COEF = 0.0001
DELTA_AZIMUTH = 25 #tolerance of key point matches

def check_H(h):#ytf
    """
    Checks homography matrix 'sanity'
    
    Args:
        h- homography matrix
    Returns:
        True for valid matrix, else false
    """
    print('check h')
    print(h)
    return True

def filter_kp_by_azimuth (kp1,kp2,matches,azimuth):
    """
    Filters matched key-points by the GPS azimuth between two images
    Args:
        kp1,kp2,matches - key-point and matches as given in opencv format
    Returns:
        kp1,kp2,matches - valid key point matches in opencv format
    """
    # azimuth = (azimuth+180)%360
    #find azimuth between key pts    
    base_kp = [kp1[mat.queryIdx].pt for mat in matches]
    img_kp = [kp2[mat.trainIdx].pt for mat in matches]
    pts1 = [Point(kp1[mat.queryIdx].pt[0],kp1[mat.queryIdx].pt[1])
            for mat in matches]
    pts2 = [Point(kp2[mat.trainIdx].pt[0],kp2[mat.trainIdx].pt[1])
            for mat in matches]
    az_list = [pts2[i].azimuth(pts1[i]) for i in range (len(pts1))]
    indexes = [i for i in range (len(az_list)) if
               (abs(az_list[i]-azimuth)%(360-DELTA_AZIMUTH) < DELTA_AZIMUTH) or
               (abs(az_list[i]-azimuth+180)%(360-DELTA_AZIMUTH) < DELTA_AZIMUTH)]
               
    # kp1 = [kp1[i] for i in indexes]
    # kp2 = [kp2[i] for i in indexes]
    # matches = [matches[i] for i in indexes]
    base_kp = [base_kp[i] for i in indexes]
    img_kp = [img_kp[i] for i in indexes]
    matches = [matches[i] for i in indexes]
    
    return (np.array(base_kp),np.array(img_kp),matches)
    
    
def homography_by_BRISK(base,img,azimuth,show_matches = False, delta_az=DELTA_AZIMUTH):
    """
    returns homography matrix using brisk
    """
    
    gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    
    brisk = cv2.BRISK_create(thresh=100,octaves=4)
    kp1 = brisk.detect(gray1)
    kp2 = brisk.detect(gray2)

    _, des1 = brisk.compute(gray1,kp1)
    _, des2 = brisk.compute(gray2,kp2)
    
    #Hamming distance for brisk binary descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors.
    matches = bf.match(des1,des2)
    # Sort them in the order of their distance. Take the best matches
    matches = sorted(matches, key = lambda x:x.distance)
    matches = matches[:NUM_OF_MATCHES]
    
    img3 = cv2.drawMatches(gray1,kp1,gray2,kp2,matches,None, flags=2)
    
    (base_kp,img_kp,matches) = filter_kp_by_azimuth (kp1,kp2,matches,azimuth)
    # valid_matches2 = valid_matches[np.where(abs()]
    #valid_base,img_kp -> .pt
    (H, status) = cv2.findHomography(base_kp, img_kp,
                                     method=cv2.RANSAC, ransacReprojThreshold=10)
    if (show_matches):
        print('H----------------')
        print(H)
        print ('BASE',len(base_kp))
        print('img',len(img_kp))
        print ('match',len(matches))
        img4 = cv2.drawMatches(gray1,kp1,gray2,kp2,matches,None, flags=2)

        # img5 = cv2.drawMatches(gray1,kp1,gray2,kp2,valid_matches,None, flags=2)
        ax = plt.subplot (211)
        ax.imshow (img3)#[...,::-1])
        plt.title ('original matches '+str(len(matches)))

        plt.subplot (212,sharex = ax,sharey = ax)
        plt.imshow (img4)#[...,::-1])
        plt.title ('directional matches'+str(len(matches)))
        
        plt.show()
        
    
    if check_H(H):
        return H
    else:
        return None
        
def stitch_2 (base,img,azimuth,show_matches = True):
    """
    Stitches img2 (img) to img1 (base), on img1 plane, using homography matrix H.
    Parameters:
        base image, stitched image
        
    Returns:
        stitched image
     
    Returns type:
        image (a 3D np.array )

    """
    if (img is None): #img is empty
        print ('none img')
        return base
    H = homography_by_BRISK (base,img,azimuth,show_matches)
    if (H is None):
        print ('none homo')
        return base
    #calc coordinates of joined image
    Ybmax,Xbmax = base.shape[:2]
    h,w = img.shape[:2]
    
    P = np.array([[0,w,w,0],
                  [0,0,h,h],
                  [1,1,1,1]])
    HP = np.dot(H,P)
    #find coordinates of the warped image corners
    xcoor = HP[0,...]/HP[2,...]
    ycoor = HP[1,...]/HP[2,...]
    #############################
    # print (xcoor)
    # print(ycoor)
    
    ##############################
    Ximin = int(min(xcoor))
    Ximax = int(max(xcoor))
    Yimin = int(min(ycoor))
    Yimax = int(max(ycoor))
    #######################
    # print ('x,y, vals')
    # print (Ximin,Ximax,Yimin,Yimax)
    # print (Xbmax,Ybmax)
    
    #########################
    x_shift = abs(min(0,Ximin))
    y_shift = abs(min(0,Yimin))
    
    Xjoined = x_shift + max(Xbmax,Ximax)
    Yjoined = y_shift + max(Ybmax,Yimax)
    
    result = np.zeros((Yjoined,Xjoined,3))
    ####################
    # print ('x,y',Xjoined,Yjoined)
    # print ('shift', x_shift,y_shift)
    ####################
    #shift and warp
    M = np.float32([[1,0,x_shift],[0,1,y_shift]])
    shifted = cv2.warpAffine(img,M,(Xjoined,Yjoined))
    # plt.imshow(shifted),plt.show()
    warpped = cv2.warpPerspective(shifted, H, (Xjoined,Yjoined))
    # plt.imshow(warpped),plt.show()
    result = np.copy(warpped)
    #'print' base image,without black holes
    coords = np.where(base!=[0,0,0])
    coords0 = coords[0] + y_shift
    coords1 = coords[1] + x_shift
    coordstag = (coords0,coords1,coords[2])
    result[coordstag] = base[coords]
    # result[y_shift:(Ybmax+y_shift),x_shift:(Xbmax+x_shift)] = base
    
    
    # ax = plt.subplot (141)
    # ax.imshow (warpped)#[...,::-1])
    # plt.title ('warped')

    # plt.subplot (142,sharex = ax,sharey = ax)
    # plt.imshow (base)#[...,::-1])
    # plt.title ('base')

    # plt.subplot(143,sharex = ax,sharey = ax)
    # plt.imshow(result)
    # plt.title('res')

    # plt.subplot(144,sharex = ax,sharey = ax)
    # plt.imshow(final)
    # plt.title('final')
    
    # plt.show()
    # plt.imshow(result),plt.show()
    
    return result
    
def align_north(img,azimuth):
    """
    """
    rows,cols = img.shape[:2]
    if azimuth > 180 :
        azimuth = azimuth - 360 # negetive values for clockwise rotation
    M = cv2.getRotationMatrix2D((cols/2,rows/2),azimuth,1)
    
    dst = cv2.warpAffine(img,M,(cols,rows))
    return  (dst)
    
def stitch_n (img_list,azimuth):

    """
    stitches list of images using stitch_2 func
    """
    result = img_list[0]
    for i in range (1,len(img_list)):
        result = stitch_2(result,img_list[i],azimuth,show_matches=False)
    # result = align_north (result,azimuth)
    return result
    
    
def stitch_slice(slice):
    """
    """
    print ('stitch_slice',slice)
    #sort by x center value
    # slice.sort(key = lambda im:im.center.x)
    azimuth = slice[0].center.azimuth(slice[-1].center)
    new_center = slice[0].center.mid_pt(slice[-1].center)
    im_list = []
    for im in slice:
        print ('num {} az{}'.format(im.num,im.next_azimuth))
        if (90 < im.next_azimuth < 270):
            im_list.append(cv2.resize((im.get_image(fliped=True)),(800,600)))
            print ('fliped')
        else:
            im_list.append(cv2.resize((im.get_image(fliped=False)),(800,600)))
            print ('not fliped')
    print('len im list',len(im_list))
    for im in im_list:
        print (type(im))
    res = stitch_n(im_list,azimuth)
    return res
    
    
    
def build_slices_matrix (slices,images):
    """
    """
    slice_mat = []
    for sl_row in slices:
        slice_row = []
        for slice in sl_row:
            sl_images = [images[i] for i in slice]
            im = stitch_slice (sl_images)
            plt.imshow(im),plt.show()
            slice_row.append(im)
        slice_mat.append(slice_row)
    return slice_mat

    
if __name__ == '__main__':
    # mypath = prefix = 'C:\\Users\\eran\\mystuff\\imageproc\\hafetz\\080718\\all\\DJI_'
    mypath ='C:\\Users\\eran\\mystuff\\imageproc\\code\\ver7\\tests\\'

    # start = int(sys.argv[1])
    # end = int(sys.argv[2])

    filelist =  os.listdir(mypath)
    print (filelist)
    # images = io.extract_meta_data(mypath)
    #get the pics - only for check!!1
    images = io.extract_meta_data (mypath)
    pics = []
    for im in images:
        pics.append(cv2.resize(cv2.imread(im.full_name),(800,600)))
    az = images[0].center.azimuth(images[-1].center)
        
    # az = 90#images[0].azimuth (images[-1])
    print ('az',az)
    # print (images[0].center,images[1].center)
    im = stitch_n(pics,az)
    plt.imshow(im),plt.show()
    cv2.imwrite(mypath+'res.jpg',im)
