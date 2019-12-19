"""
Arranges images by location and finds pixel sizes of an image
"""


#cv and math imports
import numpy as np
from matplotlib import pyplot as plt
import cv2

#metadata, locations
import PIL.ExifTags
import PIL.Image

from math import radians, cos, sin, asin, sqrt,atan,atan2,degrees,inf
import time
import os
import re
import sys
import utm #latqlong to utm-wgs84 transformations
from copy import deepcopy

import in_out as io
import constants as const
import stitching as st
import utilmod as util

from classes import Point,Image,Route,Pano,Target

def break_point (vals,eps):
    """
    returns the index of the first value item that differs in more
    then epsilon
    
    Args:
        vals: list of values
        eps: tolerance
        
    Returns:
        index of break point, len (vals) if none exists
    """
    
    for i in range (len(vals)-1):
        if  (eps < abs (vals[0]-vals[i]) < (360-eps)):
            return i
    return len(vals) #end of list

def in_routes(images,routes):
    """
    Clears all images *not* in route from images list.
    
    Args:
        images: list of images (Image obj)
        routes: list of routes (Route obj)
    Returns:
        tuple of images list, and routes list
    """
    # print ('---------------in_routes------------')
    out_images_num = 0
    last_img = -1
    in_route_images =[]
    for r in routes:
        # print (last_img, r.first_index,out_images_num,len(in_route_images))
        out_images_num += r.first_index - (last_img + 1)
        #copy images in route
        in_route_images.extend (images[r.first_index:r.last_index+1])
        last_img = r.last_index
        #update indexes
        r.first_index -= out_images_num
        r.last_index -= out_images_num
    return (in_route_images,routes)
    # route_ind = []
    # in_images = []
    # for r in routes:
        # indexes = list (range(r.first_index,r.last_index+1))
        # route_ind.extend(indexes)
    # for i in route_ind:
        # in_images.append(images[i])
    # return in_images
    
    
def slice_size (locmat):
    """
    Find the index of bits. returns a tuple of 2 list of rows
    and columns indexes
    """
    height,width = locmat.shape
    num_of_routes = 20 ######################################################
    num_of_images = 50  ######################################################
    route_width = width/num_of_routes
    im_height = height/num_of_images
    route_slice = [int(route_width*i) for i in range(num_of_routes)]
    route_slice.append(width)
    im_slice = [int(im_height*i) for i in range(0,num_of_images,const.BATCH_SIZE)]
    im_slice.append(height)
    return (im_slice,route_slice)

    
    

def extremes (pts):
    """ Finds extremes in list"""
    minx = min ([p.x for p in pts])
    maxx = max ([p.x for p in pts])
    miny = min ([p.y for p in pts])
    maxy = max ([p.y for p in pts])
    
    return (minx,maxx,miny,maxy)
################################################
def validate_routes (routes): ##################   
    return (routes)
################################################    
def get_routes(images,offset):
    """
    Calculate the flight paths, using the direction between consequent
    images.
    Args:
        Image instances list
        the most south image coordinate
    Returns:
        list of routes
    
    """
    print ("Getting routes")
    t1 = time.time()
    routes = []
    #get azimuths between images
    azimuths = []
    for i,image in enumerate(images[:-1]):
        image.set_next_azimuth(images[i+1])
        image.set_next_distance(images[i+1])
        azimuths.append(image.next_azimuth)
    images[-1].next_azimuth = images[-2].next_azimuth
    #get the routes
    start = 0
    end = 0
    while (end < len(azimuths)):
        end = start + break_point(azimuths[start:],const.DIRECTION_ACCURACY)
        if ((end - start) > const.MIN_IMAGES_IN_ROUTE): #filter non valid courses
            # print (start,end)
            routes.append(Route(images[start],images[end],(start,end),offset))
        start = end+1
        # directions = directions[start:]
        
    t2 = time.time()
    #set azimuth of end images
    for r in routes:
        r.end.next_azimuth = r.start.next_azimuth
        for i in range(r.first_index,r.last_index):
            images[i].next = images[i+1]
            images[i+1].prev = images[i]
    print("got {} routes in {} sec...".format(len(routes),t2-t1))  
    return routes

def find_routes(images):
    """
    Finds routes of images - gets routes and then validates them.
    
    Args:
        images: images list (Image obj)
    Returns:
        list of routes (Route obj)    
    """

    extr = extremes ([im.center for im in images])
    offset = Point(extr[0],extr[2])
    routes = get_routes (images,offset)
    routes = validate_routes (routes)
    l_route = routes[0]
    for r in routes[1:]:
        if r.length > l_route.length:
            l_route = r
    # for im in images:
        # im.set_fliped (l_route.start.next_azimuth)
    return(routes)

def polygon_area(vertices):
    """Calculate the area of the vertices described by the sequence of vertices.
    Thanks to Darel Rex Finley: http://alienryderflex.com/polygon_area/
    """
    area = 0.0
    X = [float(vertex.x) for vertex in vertices]
    Y = [float(vertex.y) for vertex in vertices]
    j = len(vertices) - 1
    for i in range(len(vertices)):
        area += (X[j] + X[i]) * (Y[j] - Y[i])
        j = i
    return abs(area) / 2  # abs in case it's negative
    
def get_area (route_lst):
    """
    Area of routes list
    """
    routes = deepcopy(route_lst)
    routes.sort(key = lambda r: r.intersection)
    vertices = []
    for r in routes:
        if (90 < r.start.next_azimuth < 270):
            vertices.append(r.start_pt)
        else:
            vertices.append(r.end_pt)
    routes = routes[::-1]
    for r in routes:
        if (90 < r.start.next_azimuth < 270):
            vertices.append(r.end_pt)
            # print (r.end.num)
        else:
            vertices.append(r.start_pt)
            # print (r.start.num)

        vertices.append(r.end_pt)
    area = polygon_area(vertices)
    return area
        
def build_loc_dict (sils,delete_far_sils=True):
    """
    Builds location dictionary for silhouettes, in which for every sil there
    is a list of all close other silhouettes.
    """
    loc_dict = {}
    extr = extremes ([s.xy_center for s in sils])
    minx = extr[0]
    maxy = extr[3]
    for i,s in enumerate(sils):
        delete = False
        if delete_far_sils: 
            m = s.image.center_pxl
            if ((abs(s.center.x - m.x) < m.x/2) and
               (abs(s.center.y - m.y) < m.y/2)):
               delete = True
               # print ('deleted')
        if not(delete):
            x = int(round(s.xy_center.x))
            y = int(round(s.xy_center.y))
            k = str(x)+str(y)
            v = i
            if (k in loc_dict):
                loc_dict[k].append(i)
            else:
                loc_dict[k] = [i]
    # print (loc_dict)
    return loc_dict
    
def join_silhouette (sils):
    """
    Joins silhouettes if they are close enough, using loc_dict
    """
    # print ('---------------join silhouettes--------------')

    res = []
    middle = sils[0].image.center_pxl
    loc_dict = build_loc_dict (sils)
    # print ('len dict',len(loc_dict))
    for k in loc_dict:
        l = remove_similar (loc_dict[k],sils,middle)
        loc_dict[k] = l
        res.extend(l)
    return [sils[i] for i in res]
   
def remove_similar(inds,sils,middle):
    """
    Removes similar silhouettes
    """
    p = 0
    while (p < len (inds)):
       inds = join_first (inds[p:],sils,middle)
       p += 1
    return inds
        
def join_first (inds,sils,middle):
    """
    joins all silhouettes similar to the first one
    """
    first = inds[0]
    ninds = [first]
    for i in inds[1:]:
        res = join2sils(sils[first],sils[i],middle)
        if res < 0 :
            ninds.append (i)
        elif (res == 1):
            first = i
    ninds[0] = first
    return ninds
    
def join2sils(first,second,middle):
    """ Joins 2 silhouettes"""
    
    if not(0.75 < first.area/second.area < 1.25):
        return -1
    else:
        if first.center.distance(middle) > second.center.distance(middle):
            return 0
        else:
            return 1
            
            
def mat_rotate (mat,images):#############################################
    """
    Rotate a given location mat to north-south direction
    """
    #to be continued....
    return mat
   
   
def find_locmat (images,routes):
    """
    Create a matrix representation of all image locations
    
    Args:
        images list (Image obj.), routes list(Route obj.)
    Returns:
        tuple of 
            - matrix of location, each nonzero element is image index
              in images
            - x coordinate of top left point in matrix
            - y coordinate of top left point in matrix
    """
    extr = extremes ([im.center for im in images])
    # cast to int
    i_extr = np.asarray(extr,dtype=int)
    mat = np.zeros(((i_extr[3] - i_extr[2] + 1),
                    (i_extr[1] - i_extr[0] + 1)))
    for r in (routes):
        for i,im in enumerate(images[r.first_index:r.last_index+1]):#########  i+r.first_index
            xval = int(extr[3] - im.center.y)
            yval = int(im.center.x - extr[0])
            if (mat[xval][yval] == 0): # no other image in the same place
                mat[xval][yval] = (i+r.first_index + 1) #add 1 to differ index 0
            else:
                vacant = False
                while not(vacant):
                    xval += 1
                    vacant = (mat[xval][yval] == 0)
                mat[xval][yval] = (i+r.first_index + 1)
    # rotate to north-south direction
    mat = mat_rotate(mat,images)
    xmin = extr[0]
    ymax = extr[3]
    return (mat,xmin,ymax)

def get_slices(locmat):
    """
    get the (indexes of) images in a slice. usually hold about 5 consecutive
    images in a route, but sometimes routes intersect.
    """
    rows,cols = slice_size (locmat)
    rows = rows[:5]
    cols = cols[:5]
    #
    # print ('rows',rows)
    # print ('cols',cols)
    #
    slices = []
    #build slices mat
    for i in range(len(rows[:-1])):
        slices_row =[]
        for j in range (len(cols[:-1])):
            sector = np.array (locmat[rows[i]:rows[i+1],
                                      cols[j]:cols[j+1]])
            slice = sector[np.nonzero(sector)].astype(int).tolist()
            slices_row.append(slice)
        slices.append(slices_row)
    # print (slices)
    return slices
            

def set_pxl_size(images,routes):
    """
    Sets pxl size for all images.
    """
    # print ('Finding pixel sizes...')
    ts = time.time()
    last = 0
    for r in routes:
        pxl_sizes = []
        im_list = images[r.first_index:r.last_index+1]
        if (r.last_index > last): last = r.last_index
        # print (len(im_list))
        first = im_list[:-1:const.PXL_CALC_LEAP]#every some images in route
        second = im_list[1::const.PXL_CALC_LEAP]
        for i,f in enumerate(first):
            pxl_sizes.append(p_size(f,second[i]))
        pxl_average = [(pxl_sizes[i]+pxl_sizes[i+1])/2 for 
                        i in range(len(pxl_sizes)-1)]
        pxl_average.append(pxl_sizes[-1])
        for i,im in enumerate(im_list):
        #######################
            im.pxl_size = pxl_average[int(i/6)]
    for im in images[last:]:
        if (im.pxl_size ==1):
            im.pxl_size = pxl_average[-1]
    te = time.time()
    print ('found pixel sizes in {} seconds'.format(te-ts))
          
def set_pixel_size(images,routes):
    """
    Sets pxl size for all images.
    Args:
        images list (only images in routes)
        routes
    returns:
        nothing. changes pxl sizes
    """
    print ('Finding pixel sizes...')
    ts = time.time()
    last_index = 0
    #find pxl size for each route 
    for r in routes:
        r_images = images[r.first_index:(r.last_index + 1)]
        pxl_sizes = [p_size(r_images[i],r_images[i+1]) for 
                        i in range(len(r_images)-1)]
        #add pxl size for last image
        pxl_sizes.append (pxl_sizes[-1])
        #moving average
        pxl_sizes = util.moving_av(pxl_sizes,const.MOVING_AVERAGE_PARAM)
        for i,im in enumerate (r_images):
            im.pxl_size = pxl_sizes[i]
        # print ('route done')
        # im_list = images[r.first_index:r.last_index+1]
        # if (r.last_index > last): last = r.last_index
        # print (len(im_list))
        # first = im_list[:-1:const.PXL_CALC_LEAP]#every some images in route
        # second = im_list[1::const.PXL_CALC_LEAP]
        # for i,f in enumerate(first):
            # pxl_sizes.append(p_size(f,second[i]))
        # pxl_average = [(pxl_sizes[i]+pxl_sizes[i+1])/2 for 
                        # i in range(len(pxl_sizes)-1)]
        # pxl_average.append(pxl_sizes[-1])
        # for i,im in enumerate(im_list):
        ######################
            # im.pxl_size = pxl_average[int(i/6)]
    # for im in images[last:]:
        # if (im.pxl_size ==1):
            # im.pxl_size = pxl_average[-1]
    te = time.time()
    print ('found pixel sizes in {} seconds'.format(te-ts))

def p_size(image1,image2):
    """
    finds pixel size between image1,image2, using matches found by BRISK alg' 
    Args:
        two images image1, image 2 (Image obj)
    Returns:
        pxl_size (in meters)
    """
    meter_dis = image1.center.distance(image2.center)
    #find pixel distance by matching
    gr1 = cv2.cvtColor(image1.get_image(), cv2.COLOR_BGR2GRAY)
    gr2 = cv2.cvtColor(image2.get_image(), cv2.COLOR_BGR2GRAY)
    
    gray1 = cv2.resize(gr1,None,fx=const.SCALE_FACTOR,fy=const.SCALE_FACTOR)
    gray2 = cv2.resize(gr2,None,fx=const.SCALE_FACTOR,fy=const.SCALE_FACTOR)
    
    #brisk match
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
    matches = matches[:const.NUM_OF_MATCHES]
    #find matches distances
    pts1 = [Point(kp1[mat.queryIdx].pt[0],kp1[mat.queryIdx].pt[1])
            for mat in matches]
    pts2 = [Point(kp2[mat.trainIdx].pt[0],kp2[mat.trainIdx].pt[1])
            for mat in matches]
    distances = [pts2[i].distance(pts1[i]) for i in range (len(pts1))]
    az_list = [pts2[i].azimuth(pts1[i]) for i in range (len(pts1))]
    distances = util.reject_outliers(distances)
    azimuths = util.reject_outliers(az_list)
    az = sum(azimuths)/len(azimuths)
    
    pxl_dis = sum(distances)/len(distances)/const.SCALE_FACTOR
    psize = meter_dis/pxl_dis
    y_shift = int (pxl_dis * cos(radians(az)))
    x_shift = int (pxl_dis * sin(radians(az)))
    image1.set_shift (-x_shift,-y_shift,image2.num)
    image2.set_shift (x_shift,y_shift,image1.num)

    return psize
            
def neighbours(ind,locmat,d):
    """
    Finds all neighbours in distance d of a given index in the location matrix
    
    Args:
        ind: index of image
        locmat: location matrix
        d: distance
    Returns:
        inds: list of indexes
    """
    maxr,maxc = locmat.shape
    i,j = np.where (locmat == (ind + 1))
    i = i[0]
    j = j[0]
    locmat[i][j] = 0 # to discard later
    rl = max(0,i-d)
    rh = min(maxr,i+d+1)
    cl = max(0,j-d)
    ch = min(maxc,j+d+1) 
    n_mat = locmat[rl:rh,cl:ch]
    inds = (n_mat[np.nonzero(n_mat)]-1).tolist()
    inds = [int(i) for i in inds]
    return (inds)
    
def same_route (im1,im2,routes):
    """
    Returns True if images are in the same route, False otherwise
    """
    for r in routes:
        if (r.start.num <= im1.num <= r.end.num): # im1 in route r
            if (r.start.num <= im2.num <= r.end.num):
                return True
            else:
                return False
    
def find_shift (image1,image2,routes):
    """
    Finds shift between two images
    """
    # check if already exists 
    if str (image2.num) in image1.shifts:
        return image1.shifts[str(image2.num)]
    shift = (0,0)
    if same_route (image1,image2,routes):
        if (image1.num > image2.num):
            img = image1
            while not(img is image2):
                c_shift = img.shifts[str(img.prev.num)]
                shift = util.add_tuple(shift,c_shift)
                img = img.prev
        else:
            img = image1
            while not(img is image2):
                c_shift = img.shifts[str(img.next.num)]
                shift = util.add_tuple(shift,c_shift)
                img = img.next
        return shift
    else: # not same route
        # find the "closest" image in next route 
        closest = find_closest (image1,image2.prev,image2,image2.next)
        #find shift to closest and to his nexts
        p = p_size(image1,closest)
        if (closest.prev):
            shift1 = image1.shifts[str(closest.num)]
            shift2 = closest.shifts[str(closest.prev.num)]
            sumshift = tuple(map(sum,zip(shift1,shift2)))
            image1.shifts[str(closest.prev.num)] = sumshift
            closest.prev.shifts[str(image1.num)] = (-sumshift[0],-sumshift[1])
        if (closest.next):
            shift1 = image1.shifts[str(closest.num)]
            shift2 = closest.shifts[str(closest.next.num)]
            sumshift = tuple(map(sum,zip(shift1,shift2)))
            image1.shifts[str(closest.next.num)] = sumshift
            closest.next.shifts[str(image1.num)] = (-sumshift[0],-sumshift[1])
    
    return (image1.shifts[str(image2.num)])
    
def  find_closest (im,*tarlist):
    """
    finds find closest targetlist item to image
    """
    mindis = inf
    minind = -1
    for i,target in enumerate(tarlist):
        if (target):
            dis = im.center.distance(target.center)
            if dis < mindis:
                mindis = dis
                minind = i
    return tarlist[minind]
        
    
    
    
    
    