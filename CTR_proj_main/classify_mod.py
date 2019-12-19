"""
Holds all classification functions
"""


#cv and math imports
import numpy as np
from matplotlib import pyplot as plt
import cv2
from math import radians, cos, sin, asin, sqrt,atan,atan2,degrees

#metadata, locations
import PIL.ExifTags
import PIL.Image
import utm #latqlong to utm-wgs84 transformations

#general libs
import pickle
import time
import os
import re
import sys
from pathlib import Path

#programs imports
import in_out as io
import constants as const
import utilmod as util

# def check_size (cont):
    # return cont
    
# def check_shape (cont):
    



def kill_small_conts(contours,hierarchy,pxl_size):
    """
    Deletes all contours smaller than a given size
    Args:
        contours: contours list
        hierarchy: contours hierarchy list in opencv format
        pxl_size: pixel size of the image
    Returns:
        tuple of (the big enough) contoures and matched hierarchy
    """
    conts = []
    hier = []
    min_pxl_area = const.MIN_LEAF_AREA/pxl_size**2 
    for i,c in enumerate(contours):
        if (cv2.contourArea(c) > min_pxl_area):
            conts.append(c)
            # hier.append(hierarchy[i])
         
    return (conts,hier)

def kill_nested_in_big (contours,hierarchy,max_size = 120000):
    """
    Deletes all contours that are big enough and their descendants. 
    Used to delete artificial contours.
    Args:
        contours: contours list
        hierarchy: contours hierarchy list in opencv format
        max_size: in pixels
    Returns:
        tuple of (the big enough) contoures and matched hierarchy, 
        and artificial contours

    """
    ts = time.time()
    del_indexes = []
    conts = []
    hier = []
    art_conts = []
    # find all sons
    
    for i,c in enumerate(contours):
        if((cv2.contourArea(c) > max_size)):
            # and util.solidity (c) > const.MIN_ARTIFICIAL_SOLIDITY ):
            art_conts.append(c)
            # print ('tree list of {} '.format(i),hierarchy[i])
            sons = util.tree_list(conts,hierarchy,i)
            del_indexes.extend(sons)
    # delete the sons
    red_conts = [c for i, c in enumerate(contours) if i not in del_indexes]
    red_hier = [h for i, h in enumerate(hierarchy) if i not in del_indexes]
    te = time.time()
    return (red_conts,red_hier,art_conts)
            
# def classify_conts (image,conts,hierarchy):
    # c,h = kill_big_and_nested (contours,hierarchy)
    # c,h = kill_small_conts (c,h)
    ## 
    # return c,h
 
def bare_soil(sil):
    """Returns True if the conture is of bare soil
    """
    sil.get_color_params()
    if ((sil.l_mean < 160) and (sil.a_std > 3)):
        return False
    else:
        return True
  
def bare_soil_cont (c,im):
    x,y,w,h = cv2.boundingRect(c)
    stamp = np.copy (im [y:y+h,x:x+w])
    lab_stamp = cv2.cvtColor(stamp, cv2.COLOR_BGR2Lab)
    l_channel = lab_stamp[:,:,0]
    a_channel = lab_stamp[:,:,1]
    c = c - (x,y)

    mask = np.zeros((h,w))
    cv2.drawContours(mask,[c],0,255,-1)
    # plt.imshow(mask),plt.show()
    pts = np.where(mask == 255)
    l_lst = l_channel[pts[0],pts[1]]
    a_lst = a_channel[pts[0],pts[1]]
    if ((np.mean(l_lst) < 160) and (np.std(a_lst) > 3)):
        return False
    else:
        return True 
        
def main_classifier (image,conts,hierarchy,pxl_size = -1):
    """
    Classify all conts in an image, to artificial/bare-soil/targets
    
    Args:
        image: image object
        conts: raw list of contours, as recived after filtering
        hierarchy: hierarchy list in opencv format
        pxl_size: pxl size of the image
    Returns:
        tuple holding the lists of the artificial/bare-soil/targets contours
    """
    ts0 = time.time()
    art_conts = []
    bare_soil_conts = []
    target_conts = []
    del_indexes = []
    t1 = time.time()
    im = image #.get_image()
    t2 = time.time()
    artificial_pxl_size = const.MAX_ARTIFICIAL_TRUE_SIZE / (pxl_size**2)
    te0 = time.time()
    ts = time.time()

    conts, hierarchy,art_conts = kill_nested_in_big (conts,hierarchy,artificial_pxl_size)
    te = time.time()
    conts, hierarchy = kill_small_conts(conts, hierarchy,pxl_size)
    # print ('all conts',len(conts))
    #delete the sons of artificial contours
    for c in (conts):
        if (bare_soil_cont(c,im)):
            bare_soil_conts.append(c)
        else:
            target_conts.append(c)
    # print ('art {} bare {} targets {}'.
        # format(len(art_conts),len(bare_soil_conts),len(target_conts)))
    
    return (art_conts, bare_soil_conts,target_conts)

    
    
    
    
    
    
