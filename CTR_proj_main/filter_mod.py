


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

from classes import *
import in_out as io
import constants as const
import utilmod as util
import classify_mod as cls
import filter_mod as flt

def validate_browns(contours,hierarchy):
    """
    """
    return (contours,hierarchy)

def lab_filter (img,eq=False,TL=60,TA=127):
    """
    Applies contour finding in a filtered image using LAB color space
    Args:
        img: the image itself (*not* image object)
        eq: boolean- if True performs histogram equalization to the image
        prior to the fitering and contours finding
        TL - threshold for l channel
        TA: - threshold for a channel
    Returns:
        tuple of contours and hierarchy
    """

    l_img = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    
    if (eq):
        blurredL = cv2.GaussianBlur(cv2.equalizeHist(l_img[...,0]),(5,5),5)
        blurredA = cv2.GaussianBlur(cv2.equalizeHist(l_img[...,1]),(5,5),5)
        blurredB = cv2.GaussianBlur(cv2.equalizeHist(l_img[...,2]),(5,5),5)
        TL = 60
        TA = 160

    else:
        blurredL = cv2.GaussianBlur(l_img[...,0],(5,5),5)
        blurredA = cv2.GaussianBlur(l_img[...,1],(5,5),5)
        blurredB = cv2.GaussianBlur(l_img[...,2],(5,5),5)
        TL = 60
        TA = 127
        
    retL,threshL = cv2.threshold(blurredL,TL,255,cv2.THRESH_BINARY)
    reta,thresha = cv2.threshold(blurredA,TA,255,cv2.THRESH_BINARY)
    
    thresh = cv2.bitwise_and(threshL,thresha)
   

    contours,hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)#*********change 2nd parameter******************
    ###########
    return (contours,hierarchy)

def find_browns (image,break_tiles=True,tile_size=const.TILE_SIZE):
    """
    Find brown regions in an image.
    Args:
        image (an Image instance)
        
    Returns:
        
    """
    # print('filter brown objects...')
    img = np.copy(image.get_image())
    if (img is None):
        print("unable to open image")
    # print ('----------find_browns-------------')
    img_size = img.shape[0]*img.shape[1]
    if (break_tiles):
        tiles = util.divide (img,tile_size,0)
    else:
        tiles = [Tile((0,0),(0,0),image.get_image().shape[:2])]
    # print ('tiles',len(tiles))
    #find regions in every tile
    # im_conts = []
    # raw_conts = []
    # im_hier = []
    total_art = []
    total_soil = []
    total_targets =[]
    
    flt_time = 0
    cls_time = 0
    all_time = 0
    t0 = time.time()
    ts = t0
    for tile in tiles:
        # print ('tile')
        im = img[tile.topleft.y:(tile.topleft.y+tile.dim[1]),
                      tile.topleft.x:(tile.topleft.x+tile.dim[0])]
        contours,hierarchy = flt.lab_filter(im)
        tf = time.time()
        # print ('len contours', len(contours))
        if (len(contours) > 0):
            art_conts, bare_soil_conts,target_conts = cls.main_classifier(img,
                contours,hierarchy[0],image.pxl_size)
            tc = time.time()
        # if (len(contours) > 0):
            # hierarchy = hierarchy[0]
            # print ('conts',len(contours))
            #delete very small contours for efficiency
            # conts,hierarchy = cls.kill_small_conts(contours,hierarchy)
            # delete very big contours (considered artificial)
            # print ('conts',len(conts))
            # conts,hierarchy = cls.kill_big_and_nested (conts,hierarchy,
                                # max_size=0.15*img_size)
            # print ('conts',len(conts))
            # raw_conts.extend(conts)
            offset = (tile.topleft.x,tile.topleft.y)
            # for c in conts:
                # if (len(c)>0):
                    # os_c = np.array(c)+offset
                    # os_c = os_c.tolist()
                    # os_conts.append(os_c)
            # if (len(conts) > 0):
            total_art.extend(util.add_offset (art_conts,offset))
            total_soil.extend(util.add_offset (bare_soil_conts,offset))
            total_targets.extend(util.add_offset (target_conts,offset))
            cls_time += tc - tf
        flt_time += tf - ts    
        ts = time.time()
        
    all_time = time.time() - t0
    # print ('img{} total'.format(image.num), len(im_conts))
    # im_sils = []
    # for c in im_conts: #create silhouettes list
        # sil = Silhouette(image,c)
        # im_sils.append(sil)
    # print ('done filtering. all time is {} seconds, filtering took {} sec, class took {} seconds'.format(
        # all_time,flt_time,cls_time))
    return (total_art,total_soil,total_targets)
    
def find_blacks (img):
    """
    Returns number of black pixels in image
    """
    dim = img.shape
    all_pxls = dim[0]*dim[1]
    nonblacks = np.count_nonzero(img)
    return (all_pxls - int(nonblacks/3))




