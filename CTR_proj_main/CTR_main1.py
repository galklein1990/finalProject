"""
Finds targets in cotton fields. Targets are bare soil or brown bushes.
the program saves all processed data to specified file, if none given the program creates a file 
inside the working directory.
Processed data includes images (saved as jpg files), txt files, xlsx files, and orthophoto image
(as jpg). The program also saves pickle binary files.


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
#gui
from appJar import gui
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
import images as imgmod
import one_image
from classes import *

# mode = io.get_mode()
# paths = io.get_paths(mode)
tsmain = time.time()
all_conts = []
all_clusters = []
all_soil_conts = []
all_soil_clusters = []
def main_flow (mode,paths):
    print("mode =" + str(mode))
    print("paths[i] = " + str(paths))
    if (paths['output'] is None):
        paths['output'] = 'output\\'
    paths['output'] += '\\'
    if mode == "ortho":
        full_run = True
        if not (paths['pickle_file'] == ''):
            full_run = False
            try:
                # fh = open(paths['output'] + "data.pkl","rb")
                fh = open(paths['pickle_file'],'rb')
                print ('open')
                data = pickle.load(fh)
                art_conts,bare_soil_conts,target_conts,stats = data
            except:
                print ('unable to load. running as usual')
                full_run = True
                
        if (full_run):
            #only ortho - break tiles, find clusters, dont join
            print ('getting panorama...')
            pano = cv2.imread(paths["ortho"])
            scale = 1
            # print (pano.shape)
            wd = io.get_pano_data(paths["ortho_data"],scale)
            # print (wd)
            # print ('scale',scale,'wd', wd['scale'])
            image = Image(paths['ortho'],name='',coords=None,dimentions=None,
                        date=None,pxl_size=wd['xscale']/scale)
            # conts,hierarchy = flt.find_browns (image)
            art_conts, bare_soil_conts,target_conts = flt.find_browns (image)
            # cls.main_classifier(image,
                # conts,hierarchy,image.pxl_size)
            art_sils = [Silhouette(image,c,type=const.ARTIFICIAL) for c in art_conts]
            bare_soil_sils = [Silhouette(image,c,type=const.BARE_SOIL) for c in bare_soil_conts]
            target_sils = [Silhouette(image,c,type=const.TARGET) for c in target_conts]
            blacks = flt.find_blacks (pano)
            stats = util.pano_stats(pano.shape[:2],wd['xscale'],
                    art_sils, bare_soil_sils,target_sils,blacks)
            #save if new run
            fh = open(paths['output'] + "data.pkl","bw")
            pickled_data = (art_conts,bare_soil_conts,target_conts,stats)
            pickle.dump(pickled_data,fh)
            fh.close()
            
        
        #resize for easier viewing
        print (stats)
        io.save_dict_to_txt (stats, paths['output']+'results.txt')
        io.save_dict_to_xcl (stats, paths['output']+'results.xlsx')
        pano,scale = io.get_pano_img(paths['ortho'])
        a_c = [(c*scale).astype(int) for c in art_conts]        
        b_s_c = [(c*scale).astype(int) for c in bare_soil_conts]
        t_c = [(c*scale).astype(int) for c in target_conts]
        cv2.drawContours (pano,a_c,-1,(0,255,0),1)
        cv2.drawContours (pano,b_s_c,-1,(255,0,0),1)
        cv2.drawContours (pano,t_c,-1,(0,255,255),1)
        cv2.imwrite (paths['output'] + 'res_pano.jpg',pano)
        plt.imshow(pano[...,::-1]),plt.show()
        
        
    elif mode == const.ONE_PLAIN_IMAGE:
       pass

    # elif mode == "images":
        # joined_art_sils,joined_soil_sils, joined_target_sils, joined_clusters = images.process_images(paths)
        # images,locmat = imgmod.process_images(paths)
        
    elif((mode == "ortho+images") or (mode == "images")):
        print('we indeed got into otho+images')
        full_run = True
        if not (paths['pickle_file'] == ''):
            full_run = False
            try:
                # fh = open(paths['output'] + "data.pkl","rb")
                fh = open(paths['pickle_file'],'rb')
                print ('loading...')
                data = pickle.load(fh)
                images,locmat = data
            except:
                print ('unable to load. running as usual')
                full_run = True
                
        if (full_run):
            #process images and get all clusters
            images,locmat = imgmod.process_images(paths)
            # save the data
            fh = open(paths['output'] + "data.pkl","bw")
            pickled_data = (images,locmat)
            pickle.dump(pickled_data,fh)
            fh.close()

        mat = locmat[0]
        #############
        soil_clusters = []
        target_clusters = []
        for img in images:
            soil_clusters.extend([s for s in img.clusters 
                if s.type == const.BARE_SOIL])
            target_clusters.extend([s for s in img.clusters
                if s.type == const.TARGET])
                
        if (mode == "ortho+images"):
            pano,scale = io.get_pano_img(paths["ortho"])
            wd = io.get_pano_data(paths["ortho_data"],scale)
        else:
            pano,scale,wd = io.artificial_pano(locmat,images)
        
        
        
        
        for cl in soil_clusters:
            impos = util.xy2pxl (cl.xy_center,wd)
            xpos,ypos = impos.p_tuple()
            area = cl.true_area
            r = max(15,(sqrt(area) / np.pi)/(wd['xscale']*scale))
            cv2.circle(pano,(xpos,ypos),15,(0,0,255),2)

        for cl in target_clusters:
            impos = util.xy2pxl (cl.xy_center,wd)
            xpos,ypos = impos.p_tuple()
            area = cl.true_area
            r = max(15,(sqrt(area) / np.pi)/(wd['xscale']*scale))
            cv2.circle(pano,(xpos,ypos),15,(255,0,255),2)

        cv2.imwrite (paths['output']+'pano.jpg',pano)
        heat_map = util.heat_map (pano,wd,soil_clusters+target_clusters,sqr_size=10)
        cv2.imwrite(paths['output']+'heat_map.jpg',heat_map)
        temain = time.time()
        print ('done in {} hours'.format((temain-tsmain)/3600))
        sys.exit()
        print ('open interactive map')
        io.interactive_pano (heat_map,paths['output'],locmat,wd,images)

if __name__ == "main": # open without GUI      
    mode = io.get_mode()
    paths = io.get_paths(mode)
    main_flow (mode,paths)
      
