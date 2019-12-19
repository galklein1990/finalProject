"""
Input/Output utilities for ctr program
"""

import numpy as np
from matplotlib import pyplot as plt
import cv2
from math import radians, cos, sin, asin, sqrt,atan,atan2,degrees,ceil
from pathlib import Path
from classes import *
import constants as const
import utilmod as util
from openpyxl import Workbook


def get_mode():
    print ('Please enter mode: 1- Ortho, 2-Image,3-only images,4- ortho&images  ')
    mode = input('-->')
    return int(mode)

def get_paths(mode):
    if (mode == 1):
        res = get_ortho_paths()
    elif (mode == 2):
        res = get_images_io_paths('full')
    elif(mode == 3):
        res = get_images_io_paths ('dir')
    elif (mode == 4):
        res_o = get_ortho_paths()
        res_i = get_images_io_paths('dir')
        print (res_i,res_o)
        res = {**res_i,**res_o}
    else:
        print ('unknown mode')
        return (None)
    print (res)
    print ('Enter output path: ')
    output_path = input('-->')
    res["output"] = 'output'
    res["output"] = res["output"] + '\\'
    return res
    
def get_ortho_paths():
    print ('Enter orthophoto path: ')
    ortho_path = input('-->')
    print ('Enter orthophoto data path: ')
    ortho_data_path = input('-->')
    # ortho_path = "F:\\project\\Mosaic\\2018-08-09\\2018-08-09 Yad-Binyamin RGB UTM OneButton_1.tif"
    # ortho_data_path = "F:\\project\\Mosaic\\2018-08-09\\2018-08-09 Yad-Binyamin RGB UTM OneButton_1.tfw"
    ortho_path = "F:\\project\\MosaicHires\\18-7-18.jpg"
    ortho_data_path = "F:\\project\\MosaicHires\\2018-07-18 Yad-Binyamin RGB UTM OneButton_Georeferenced.tfw"
    # ortho_path = "F:\\project\\MosaicHires\\8-7-18.jpg"
    # ortho_data_path = "F:\\project\\MosaicHires\\2018-07-08 Yad-Binyamin RGB UTM OneButton_1.tfw"
    # ortho_path = "F:\\project\\MosaicHires\\14-06-18.jpg"
    # ortho_data_path = "F:\\project\\MosaicHires\\Iftach 2018-06-14 RGB OneButton_1.tfw"

    
    # ortho_path = "F:\\project\\MosaicHires\\14-06-18.jpg"
    # ortho_data_path = "F:\\project\\MosaicHires\\Iftach 2018-06-14 RGB OneButton_1.tfw"
    # ortho_path = "F:\\project\\Mosaic\\2018-08-09\\2018-08-09 Yad-Binyamin RGB UTM OneButton_1.tif"
    # ortho_data_path = "F:\\project\\Mosaic\\2018-08-09\\2018-08-09 Yad-Binyamin RGB UTM OneButton_1.tfw"
    return {"ortho" : ortho_path , "ortho_data" : ortho_data_path}

def get_images_io_paths(s):

    print ('Enter {} images path: '.format(s))
    image_path = input('-->')
    
    # image_path = 'C:\\Users\\eran\\mystuff\\imageproc\\hafetz\\090818\\all\\'
    # image_path = 'F:\\project\\images\\2017-8-15-Vulcani-Kutna-Revadim-RGB\\'
    # image_path = 'F:\\project\\images\\2016-8-11-Nachsholim-50mm-65m\\'
    image_path = 'sampleInput\\'
    return {"image_path" : image_path}
    
def make_new_dir (mypath):
    p = Path(mypath)
    if not (p.exists()):
        p.mkdir()
        
def get_path(inout,mode=0):
    """
    """
    if (inout == 'in'):
        # mypath = 'F:\\project\\mosaicHires\\14-06-18.jpg'
        # mypath = 'F:\\project\\mosaicHires\\cropped_14-06-18.jpg'
        # mypath = 'C:\\Users\\eran\\mystuff\\imageproc\\code\\sandbox1\\DJI_0043.jpg'
        # mypath = 'C:\\Users\\eran\\mystuff\\imageproc\\code\\sandbox1\\DSC09214.jpg'
        mypath = 'C:\\Users\\eran\\mystuff\\imageproc\\hafetz\\090818\\all\\'
        # mypath = 'C:\\Users\\eran\\mystuff\\imageproc\\hafetz\\080718\\all\\'

    else:
        mypath = 'output\\' #gets the output path
        name = 'output'#get the name
        make_new_dir (mypath+name)
        return mypath+name
    return mypath
    
def read_exif (img):
    """
    get coordinates from exif
    """
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }

    gps = exif['GPSInfo']
    lat = gps[2]#3 2-tuples
    long = gps[4]
    height = gps[6]#2-tuple
    lat = util.todecimal(lat)
    long = util.todecimal(long)
    width = exif['ExifImageWidth']
    height = exif['ExifImageHeight']
    date = exif['DateTimeOriginal']
    return ((lat, long, height),(width,height),date)
    
def extract_meta_data (inpath): 
    """
    Extract meta data for image exif file. Assuming coordinates are
    GEO coords.

    Args:
        inpath: path to folder that holds all images
        
    Returns:
        List of Image instances
    """
    print ('Start exstracting metadata....') 
    if not(inpath[-1] == '\\'):
        inpath += '\\'
    t1 = time.time()
    pxl_size = None # util.get_pxl_size()
    images = [] # holds all images meta-data
    filelist =  os.listdir(inpath)
    print('Got files...')
    for fname in filelist:
        img = PIL.Image.open(inpath+fname)
        print ('img',img)
        coords,dimentions,date = read_exif(img)
        images.append(Image(inpath,fname,coords,dimentions,date,pxl_size))
    t2 = time.time()
    print('Got {} images in {} seconds'.format(len(images),t2-t1))
    return images

def make_images (mode,paths,wd):
    """
    Constructs images list
    """
    if ((mode == const.RAW_IMAGES) or (mode == const.IMAGES_AND_ORTHO)):
        images = extract_meta_data(paths["image_path"])
    elif (mode == const.ORTHO):
        image = Image(paths["ortho"],name='',coords = None,
            dimentions=None,date=None,pxl_size=wd['xscale'] * wd['scale'])
        dim = image.get_image().shape[:2]
        image.center_pxl = Point(int(dim[1]/2),int(dim[0]/2))
        image.center = Point(wd['topleftx']+int(dim[1]/2)*wd['xscale'] * wd['scale'],
                             wd['toplefty']+int(dim[0]/2)*wd['xscale'] * wd['scale'])
        # print ('center',image.center_pxl)
        # print ('tl is {}{}; center is {}{}'.format(wd['topleftx'],wd['toplefty'],image.center.x,
                            # image.center.y))
        images = [image]

    else:#plain image
        image = Image(paths["image_path"],name='',coords = None,
            dimentions=None,date=None,pxl_size=None)
        dim = image.get_image().shape[:2]
        image.center_pxl = Point(int(dim[1]/2),int(dim[0]/2))
        print ('center',image.center_pxl)
        images = [image]
    return images
    
def save_image(im,path,name):
    pass

def show_image_contours (img,conts):
    """
    """
    cv2.drawContours(img,conts,-1,(0,0,255),5)
    plt.imshow(img[...,::-1]),plt.title ('img  clusters'),plt.show()
    return img
    
def show_image_silhouettes (image,sils):
    """
    """
    img = image.get_image()
    plt.imshow(img),plt.show()
    conts = [s.cont for s in sils]
    cv2.drawContours(img,conts,-1,(255,0,0),5)
    plt.imshow(img[...,::-1]),plt.title ('img {} contours'.format(image.num))
    plt.show()
    return img
    
def get_pano_img (path):
    """
    """
    img = cv2.imread(path)
    maxdim = max(img.shape[:2])
    scale = 1/(ceil(maxdim/const.MAX_SHOW_DIM))
    pano = cv2.resize(img,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    return (pano,scale)
    
def get_pano_data (path,scale):
    """
    Reads tfw/jfw file.
    Args:
        path - path to file (string)
        scale - output/input ratio (if output smaller scale < 1)
    
    Returns:
        A tuple holding all parameters, x/y scale is multiplied by 
        scale parameter
    """
    keys = ['xscale','rotationy','rotationx','yscale',
            'topleftx','toplefty']
    world_data = {}
    with open(path) as tfwobj:
        for i,line in enumerate(tfwobj):
            v = line.rstrip()
            world_data[keys[i]] = (float(v))
        
    world_data['xscale'] /= scale

    world_data['yscale'] /= scale
    world_data['scale'] = scale

    return world_data
def save_dict_to_txt(dict,file_name):
    """
    """
    with open(file_name, "w") as fh:
        for k in dict:
            fh.write(k + ': ' + '{:.2f}'.format(dict[k]) +'\n' )        
    
def save_dict_to_xcl (dict,file_name):
    """
    """
    wb = Workbook()
    ws = wb.active
    ws.title = 'results'
    for k in (dict.keys()):
        row = [k,dict[k]]
        ws.append(row)
    
    wb.save(file_name)
    
def onclick(event,wd,images,locmat,output_path):
    """
    Handles click event
    """
    if (event.dblclick and event.xdata != None and event.ydata != None):
        # print ('double!')
        # print ('xdata = {}, ydata = {}'.format(event.xdata,event.ydata))
        loc = util.pxl2xy(Point(event.xdata,event.ydata),wd)
        im = util.close_tile(loc,wd,images,locmat)
        # print ('closest ',im.num,im.center)
        try:
            plt.close(2)
        except:
            print ('no window')
        fname = output_path + 'res_img{}.jpg'.format(im.num)
        image = cv2.imread(fname)
        fig2 = plt.figure(2)
        plt.imshow(image[...,::-1])
        plt.title('image {}'.format(im.num))
        fig2.show()
    

def interactive_pano (pano,output_path,locmat,wd,images):
    """
    Activates interactive panorama 
    """
    # pano = cv2.imread(pano_path)
    
    fig = plt.figure()
    locmat = locmat
    wd = wd
    images = images
    ax = fig.add_subplot(111)
    # ax = fig.add_axes([0,0,1,1])
    ax.set_title('click on points')
    ax.imshow (pano[...,::-1])
    # ax.axis([xmin,xmax,ymin,ymax])

    cid = fig.canvas.mpl_connect('button_press_event',
                lambda event: onclick(event,wd,images,locmat,output_path))
    plt.show()

def artificial_pano(locmat,images):
    """
    Builds artificial (black) panorama
    """
    mat,xmin,ymax = locmat
    image = images[0]
    pxl_size = image.pxl_size
    w = pxl_size * image.dimentions[0]
    h = pxl_size * image.dimentions[1]
    topleftx = xmin - w
    toplefty = ymax + h

    #get 'pano' size
    xmeter = mat.shape[1] + 2 * w
    ymeter = mat.shape[0] + 2 * h
    if xmeter > ymeter:
        scale = xmeter/10000
        pano = np.zeros((10000,int(ymeter/scale),3),dtype = int)
    else:
        scale = ymeter/10000
        pano = np.zeros((int(xmeter/scale),10000,3),dtype=int) 
    # get WD
    wd = {'xscale':scale, 'rotationy':0, 'rotationx':0, 'yscale':scale,
            'topleftx':topleftx, 'toplefty':toplefty }
    plt.imshow(pano),plt.show()
    return (pano,1,wd)