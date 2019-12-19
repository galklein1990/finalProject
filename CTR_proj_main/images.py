"""
Processes multiple images 
"""
#cv and math imports
import numpy as np
from matplotlib import pyplot as plt
import cv2
from math import radians, cos, sin, asin, sqrt,atan,atan2,degrees,ceil

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
import classify_mod as cls
import filter_mod as flt
import arrange
import ortho

import one_image
from classes import *

def process_images (paths):
    """
    Processes all images in a given path, saves the output
    Args:
        paths: paths dictionary
    Returns:
        images list and location matrix
    """
    images = io.extract_meta_data (paths['image_path']) 
    routes = arrange.find_routes (images)
    images,routes = arrange.in_routes(images,routes)
    locmat = arrange.find_locmat (images,routes)
    # if (0):
    # images = io.extract_meta_data (paths['image_path']) 
    # routes = arrange.find_routes (images)
    # images,routes = arrange.in_routes(images,routes)
    # locmat = arrange.find_locmat (images,routes)
    arrange.set_pixel_size (images,routes)    
    print ('Process images...')
    ts = time.time()
    # for r in routes:
        # print ('----route--------')
        # print (r.first_index,'-->',r.last_index)
        # for i in images[r.first_index:r.last_index+1]:
            # print (i.num, 'az',i.next_azimuth,'pxl',i.pxl_size)
            # print ('shifts',i.shifts)
            # if (i.next) : 
                # print ('next',i.next.num)
            # else:
                # print (i.next)
            # if (i.prev) : 
                # print ('prev',i.prev.num)
            # else:
                # print (i.prev)
   
    all_art_sils = []
    all_soil_sils = []
    all_target_sils = []
    all_clusters = []
    joined_clusters = []
    for image in images:
        # print ('image {}'.format(image.num))
        #get contours info of all 'brown' areas
        # print ('image dim',image.get_image().shape)
        # find brown contours
        art_conts, bare_soil_conts,target_conts = flt.find_browns (image,break_tiles=False)
        #classify brown contours - artificial, bare-soil, targets
        # art_conts, bare_soil_conts,target_conts = cls.main_classifier(image,conts,hierarchy,image.pxl_size)
        # get silhouettes objects
        art_sils = [Silhouette(image,c,type=const.ARTIFICIAL) for c in art_conts]
        bare_soil_sils = [Silhouette(image,c,type=const.BARE_SOIL) for c in bare_soil_conts]
        target_sils = [Silhouette(image,c,type=const.TARGET) for c in target_conts]
        for s in (art_sils + bare_soil_sils + target_sils):
            s.set_location_from_gps (image.center_pxl,image.center,
                            image.next_azimuth,image.pxl_size)

        # print ('conts in main', len (conts))
        #find clusters
        clusters = util.divide_and_find_clusters(bare_soil_sils + target_sils)

        # build silhouettes from clusters
        sil_clusters = [Silhouette(image,c[0],type=c[1]) for c in clusters]
        for s in (sil_clusters):
            s.set_location_from_gps (image.center_pxl,image.center,
                            image.next_azimuth,image.pxl_size)

        image.set_clusters(sil_clusters)
        soil_clusters = [s for s in sil_clusters if s.type == const.BARE_SOIL]
        target_clusters = [s for s in sil_clusters if s.type == const.TARGET]
        soil_clusters_conts = [s.cont for s in soil_clusters]
        target_clusters_conts = [s.cont for s in target_clusters]
        # print ('clusters',len(sil_clusters))
        # save image results
        img = image.get_image()
        cv2.drawContours (img,bare_soil_conts,-1,(255,0,255),2)
        cv2.drawContours (img,target_conts,-1,(0,0,255),2)
        # cv2.drawContours (img,soil_clusters_conts,-1,(255,0,255),13)
        # cv2.drawContours (img,target_clusters_conts,-1,(0,0,255),13)
        ###############
        # for s in soil_clusters+target_clusters:
            # p = s.center.p_tuple()
            # x,y = s.xy_center.p_tuple()
            
            # print ('x,y',x,y)
            # str1 = '{:.2f}'.format(x)[3:] + ','+'{:.2f}'.format(y)[4:]
            # print ('str1',str1)
            # cv2.putText (img,str1,p,
                        # cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,255),2)
            # str2 = str(p)
            # p2 = (p[0],p[1] + 30)
            # cv2.putText (img,str2,p2,
                        # cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,255),2)

        cv2.imwrite (paths['output'] + 'res_img{}.jpg'.format(image.num),img)
        all_art_sils.extend(art_sils)
        all_soil_sils.extend(bare_soil_sils)
        all_target_sils.extend(target_sils)
        all_clusters.extend(sil_clusters)
    # print ('clusters before join',len(all_clusters))
    # join sils
    ################# 
    # pickling
        # fh = open(paths['output']+'CTR_data.pkl','bw')
        # pickle.dump ((images,locmat),fh)
        # fh.close()
    #############
    # else:
        # fh = open(paths['output']+'CTR_data.pkl','rb')
        # images,loc = pickle.load(fh)

    
    
    
    util.join_clusters (images,routes,np.copy(locmat[0]))
    
    i = 0
    print ('writing results')
    for im in images:
        # print (im.num,'-->',len(im.clusters))
        # print (im.next_azimuth)
        # print (im.center)
        # print ('pxl',im.pxl_size)
        # print (im.shifts)
        i += len(im.clusters)
        img = im.get_image()
        clusters = [s.cont for s in im.clusters]
        # cv2.drawContours (img,clusters,-1,(0,0,255),13)
        # cv2.imwrite (paths['output'] + 'joined_img{}.jpg'.format(im.num),img)
        # print('image {} written'.format(im.num))
    # print ('total',i)
    
    # p_output = paths['output'] +'pickle\\'
    # fh1 = open (p_output + 'soil_sils.pkl','bw')
    # pickle.dump(all_soil_sils,fh1)
    # fh1.close()
    # fh2 = open (p_output + 'target_sils.pkl','bw')
    # pickle.dump(all_target_sils,fh2)
    # fh2.close()
    # fh3 = open (p_output + 'clusters.pkl','bw')
    # pickle.dump(all_clusters,fh2)
    # fh3.close()
    # fh4 = open (p_output + 'artificial.pkl','bw')
    # pickle.dump(all_art_sils,fh4)
    # fh4.close()
    te = time.time()
    print ('processed and wrote {} images in {} seconds'.format(len(images),te-ts))
    return (images,locmat)
    # return (joined_art_sils,joined_soil_sils, joined_target_sils,joined_clusters)
    
    
    
    

    