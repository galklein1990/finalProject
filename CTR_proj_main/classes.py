"""
All classes of cotton target recognition
"""
#cv and math imports
import numpy as np
from matplotlib import pyplot as plt
import cv2

#metadata, locations
import PIL.ExifTags
import PIL.Image


from math import radians, cos, sin, asin, sqrt,atan,atan2,degrees,hypot
import time
import os
import re
import sys
import utm #latqlong to utm-wgs84 transformations
import constants as mc

# import in_out as io

# import arrange_data as arrange

# import build_panorama as bp

# import stitching as st

class Point:
    """ point and its methods """
    
    def __init__(self, x, y):
        '''Defines x and y variables'''
        self.x = x
        self.y = y
        
    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def __str__(self):
        return "Point(%s,%s)"%(self.x, self.y) 
    
    def __sub__(self,other):
        return Point(self.x - other.x,
                     self.y - other.y)

    def __add__(self,other):
        return Point(self.x + other.x,
                     self.y + other.y)
    
    def mid_pt (self,other):
        return Point((self.x + other.x)/2,
                     (self.y + other.y)/2)
                     
    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return hypot(dx,dy)
    
    def azimuth (self, other):
        """
        Azimuth in degrees
        """
        dx = other.x - self.x 
        dy = other.y - self.y
        return degrees(atan2(dx,dy))%360
        
    def move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy
    def p_tuple(self):
        return (self.x,self.y)

class Image:
    """
    Holds all image meta data. Usually used when reading raw images
    (not a mosaic). 
    note : dosent hold the image itself, to use image call get_image 
    method.
    """
    
    def __init__(self,mypath,name,coords,dimentions,date,pxl_size):
        """
        Constructor.
        Args:
            mypath,name,coords,dimentions,date - all are taken from exif file
            pxl_size - initialized, to be later updated
        
        """
        self.full_name = mypath+name
        
        # self.num = #extract the  number
        if (coords): # there is an exif file
            self.num = int(re.findall(r'\d+',name)[-1])
            self.lat = coords[0] #lat,long,height
            self.long = coords[1]
            self.height = coords[2]
            self.center = Point((utm.from_latlon(self.lat,self.long)[0]),
                                (utm.from_latlon(self.lat,self.long)[1]))
            self.center_pxl = Point(int(dimentions[0]/2),int(dimentions[1]/2))
            self.dimentions = dimentions
            self.clusters = []
            self.next = None
            self.prev = None
        else: # no exif file default vals
            self.num = -1
            self.lat = None
            self.long = None
            self.height = None
            self.center = None
            self.center_pxl = None

        self.next_azimuth = 0 #
        self.date = date
        self.pxl_size = pxl_size
        self.shifts = {}
        self.homography = np.eye(3)#default
        self.corners = None
        
        
    def distance (self,other):
        return self.center.distance(other.center)
        
    def azimuth (self,other):
        return self.center.azimuth(other.center)
    
    def set_next_distance(self,next):
        """Distance to next image in route """
        self.next_distance = self.distance(next)
        
    def set_next_azimuth(self,next):
        """Azimuth to next image in route """
        self.next_azimuth = self.azimuth (next)
        
    def get_image (self,fliped=False):
        """Returns image aligned north ('northern' pixls are higher in 'image')"""
        # if (fliped):
            # return cv2.flip(cv2.imread(self.full_name),-1)
        # else:
            # return cv2.imread(self.full_name)
        if (90 < self.next_azimuth < 270):
            return cv2.flip(cv2.imread(self.full_name),-1) #flipped
        else:
            return cv2.imread(self.full_name)
            
    def get_cropped (self, x1,x2,y1,y2):
        im = self.get_image ()
        return im[x1:x2,y1:y2]
    
    def set_shift(self,x,y,other):
        k = str(other)
        v = (x,y)
        self.shifts [k] = v
        
    def set_clusters(self,clusters):
        self.clusters = clusters
    
        
class Tile:
    """holds only coordinates of a tile in an image
    """
    
    def __init__ (self,topleft,pos,dim):
        self.topleft = Point(topleft[0],topleft[1])
        self.position = (pos[0],pos[1])
        self.dim = (dim[0],dim[1])
        

class Route:
    """
    Holds the flight routes.
    """    
    
    def __init__(self,start,end,indexes,offset):
        self.start = start
        self.end = end
        self.start_pt = self.start.center - offset
        self.end_pt = self.end.center - offset
        #if general direction is downward turn the route
        self.first_index,self.last_index = indexes
        
        self.length = self.start_pt.distance(self.end_pt)
        self.ind2dis = (self.last_index-self.first_index)/self.length
        
        #self.azimuth = start.next_azimuth
        
        # looking at route as y = ax+b
        # self.a,self.b = get_a_b_arg (self)
        # teta = atan2(a,1)
    
    @property
    def slope (self):
        x0,y0 = self.start_pt
        x1,y1 = self.end_pt
        return (y1-y0)/(x1-x0)
        
    #intersection with line x = southest   
    @property
    def intersection (self):
        x0,y0 = self.start_pt.x,self.start_pt.y
        x1,y1 = self.end_pt.x,self.end_pt.y
        b = (x1*y0-x0*y1)/(x1-x0)
        a = (y1-y0)/(x1-x0)
        return (-b)/a
    
class Region:
    """
    'Skeleton' for glade and target ('bush') classes 
    note on pixel location:
        offset hold x,y values of closing rectangle of the contour
        contour coordinates ,and center, always regard the original image 
    """
    def __init__(self,num, cntr,stamp,lab_stamp,mask,
                 offset = (0,0), file_name = None,image_num = None, tile_num = None):
        self.num = num        
        self.file_name = file_name
        self.tile_num = tile_num
        self.cntr = cntr 
        self.stamp = stamp
        self.lab_stamp = lab_stamp
        self.mask = mask
        self.offset = offset
        
    def set_geometry(self):
        self.moments = cv2.moments(self.cntr)
        if self.moments['m00'] == 0: #in case contour c is a line
            self.moments['m00'] = len(self.cntr)
        self.area = self.moments['m00']
        self.center = Point(int(self.moments['m10']/self.moments['m00']),
                       int(self.moments['m01']/self.moments['m00']))
        (x,y,w,h) = cv2.boundingRect(self.cntr)
        self.solidity = self.area / (w * h)
        self.offset = (x,y)
    
    def __str__(self):
        return """for contour #{} there are {} contour pts and {} pixels\n
                  center is {}
               """.format(self.num,len(self.coor_list),len(self.area),
                self.center,self.meanR,self.meanG,self.meanBlue)

    def show_cont (self):
        """for checking
        """
        im = np.zeros(1000)
        cv2.drawContours(im,cont,-1,255,-1)
        plt.imshow(im),plt.show()
    
    def set_location_from_gps (self,im_center_pxl,im_center_utm,
                        image_azimuth,pixel_size):
        """
        Calculates the x,y (utm) coordinates of the target, using
        the gps location of the camera.
        Args:
            im_center_pxl - x,y pixel of center (as Point)
            im_center_utm - x,y utm coordinates (as Point)
            im_azimuth - azimuth/orientation of image
            pixel_size - size in meters
        Returns:
            x,y utm coordinates of the center of target (as Point)
        """
        dis = im_center_pxl.distance(self.center)
        az = im_center_pxl.azimuth(self.center)
        az = (az + image_azimuth)%360
        deltax = dis * (sin(radians(az))) * pixel_size
        deltay = dis * (-cos(radians(az))) * pixel_size
        delta = Point(deltax,deltay)
        self.xy_center = im_center_utm + delta

    
class Glade (Region):
    """
    """
    def __init__(self,num, cntr,stamp,lab_stamp,mask,
                 offset = (0,0), file_name = None,image_num = None, tile_num = None ):
        super().__init__(num, cntr,stamp,lab_stamp,mask,
                 offset, file_name,image_num, tile_num)
                 
    def set_targets(self,targets):
        self.targets = targets
    def set_leaves(self,leaves):
        self.leaves = leaves
                 
class Target(Region):    
    def __init__(self,num, cntr,stamp,lab_stamp,mask,
                 offset = (0,0), file_name = None,image_num = None,tile_num = None):
        super().__init__(image_num, cntr,stamp,lab_stamp,mask,
                 offset, file_name = None, tile_num = None)
                 
    def set_colors(self):
        
        # lab = cv2.cvtColor(self.stamp, cv2.COLOR_BGR2Lab)
        #turn pixels outside contour to zeros
        # self.lab_stamp = cv2.bitwise_and(lab,lab,self.mask)
        # self.mask = np.zeros_like(self.stamp)
        # cv2.drawContours(self.mask, self.coor_list, -1, 255, -1)#,offset=self.offset)
        # plt.imshow(self.mask),plt.show()
        # plt.imshow(self.lab_stamp),plt.show()
        
        mean_bgr,stdev_bgr = cv2.meanStdDev(self.stamp,mask=self.mask)
        mean_lab,stdev_lab = cv2.meanStdDev(self.lab_stamp,mask=self.mask)
        self.meanBlue,self.meanG,self.meanR = mean_bgr[0:3,0]
        self.meanL,self.meanA,self.meanB = mean_lab[0:3,0]
        
        self.stdevBlue,self.stdevG,self.stdevR = stdev_bgr[0:3,0]
        self.stdevL,self.stdevA,self.stdevB = stdev_lab[0:3,0]
        in_contour_coords = np.where(self.mask != 0)
        bgr_pixls = self.stamp[in_contour_coords]
        lab_pixls = self.lab_stamp[in_contour_coords]
        self.BL = bgr_pixls[...,0]
        blue,g,r = bgr_pixls[...,0],bgr_pixls[...,1],bgr_pixls[...,2]
        self.bin_blue = np.bincount(blue.ravel())
        self.bin_g = np.bincount(g.ravel())
        self.bin_r = np.bincount(r.ravel())
        self.L,self.a,self.b = lab_pixls[...,0],lab_pixls[...,1],lab_pixls[...,2]

        
        self.bin_L = self.bin_create(self.L)
        self.bin_a = self.bin_create(self.a)
        self.bin_b = self.bin_create(self.b)
    
    def bin_create (self,channel):
        bin = np.bincount(channel.ravel())
        bin[0] = 0 #ignore zeros
        bin_pad = np.zeros((260,),dtype=int)
        bin_pad[:bin.shape[0]] = bin
        return(np.sum(bin_pad.reshape(-1,10), axis=1))#
    
class Silhouette:
    """
       Holds contour,center and Image index of any Region
    """
    def __init__(self,image,cont,type = None ,istarget=True):#area
        """
        Holds referance to the image in which it was discovered, holds the contour coordinates. 
        """
        self.image = image
        self.cont = cont        
        self.moments = cv2.moments(self.cont)
        if self.moments['m00'] == 0: #in case contour c is a line
            self.moments['m00'] = len(self.cont)
        self.area = self.moments['m00']
        self.center = Point(int(self.moments['m10']/self.moments['m00']),
                       int(self.moments['m01']/self.moments['m00']))
        self.b_rect = cv2.boundingRect(self.cont) # (x,y,w,h)
        (x,y,w,h) = self.b_rect
        self.solidity = self.area / (w * h)
        self.type = type
        self.insils = []
        # self.world_center = 
    @property
    def radius(self):
        (x,y),radius = cv2.minEnclosingCircle(self.cont)
        return(int(radius))
    @property
    def world_xy_center(self):
        return (None)
        
    def set_location_from_gps (self,im_center_pxl,im_center_utm,
                        image_azimuth,pixel_size):
        """
        Calculates the x,y (utm) coordinates of the target, using
        the gps location of the camera.
        Args:
            im_center_pxl - x,y pixel of center (as Point)
            im_center_utm - x,y utm coordinates (as Point)
            im_azimuth - azimuth/orientation of image
            pixel_size - size in meters
        Returns:
            x,y utm coordinates of the center of target (as Point)
        """
       
        if (90 < image_azimuth <270): # if image was flipped
            az = image_azimuth + 180
        else:
            az = image_azimuth
            
        dis = im_center_pxl.distance(self.center)
        teta = self.center.azimuth(im_center_pxl)
        teta = (teta + az)%360
        deltax = dis * (-sin(radians(teta))) * pixel_size
        deltay = dis * (cos(radians(teta))) * pixel_size
        delta = Point(deltax,deltay)
        self.xy_center = im_center_utm + delta
    @property
    def true_area(self):
        """Area in true pxl size"""
        return (self.area * np.square(self.image.pxl_size)) # sqr.cm to sqr.m
        
    def get_color_params (self):
        """
        Finds parameters of contour pixels colors
        Args:
            self
        Returns:
            mean, std, var values in all channels
        """
        #getting contour pixels values
        #prepare a 'stamp'
        im = self.image.get_image()
        c = self.cont
        self.b_rect = cv2.boundingRect(c) # x,y,w,h
        stamp = np.copy (im [y:y+h,x:x+w])
        lab_stamp = cv2.cvtColor(stamp, cv2.COLOR_BGR2Lab)
        l_channel = lab_stamp[:,:,0]
        a_channel = lab_stamp[:,:,1]
        # prepare a mask
        mod_c = c - (x,y) # offset to fit stamp
        mask = np.zeros((h,w))
        cv2.drawContours(mask,[c],0,255,-1)
        # get pixels inside the contour
        pts = np.where(mask == 255)
        l_lst = l_channel[pts[0],pts[1]]
        a_lst = a_channel[pts[0],pts[1]]
        # set values to obj instance
        self.l_mean,self.l_std,self.l_var = np.mean(l_lst), np.std(l_lst), np.var(l_lst)
        self.a_mean,self.a_std,self.a_var = np.mean(a_lst), np.std(a_lst), np.var(a_lst)
    
    def sil_inside(self,other):
        """ True if inside """
        return ((0 < (other.center.x - self.b_rect[0]) < self.b_rect[2]) and
           (0 < (other.center.y - self.b_rect[1]) < self.b_rect[3]))
    
    def add_in_sil(self,sil):
        self.insils.append(sil)
           
class Pano:
    """
    Holds panorama /orthophoto info
    """
    def __init__(self,indexes,im):
        self.images_indexes = indexes
        self.image = im
    # def set_image(self,im):
        # self.image = im
    # def get_image (self):
        # return (self.image)
    def align_north(self,images):
        return
        # p1 = images[self.image_indexes[0]


