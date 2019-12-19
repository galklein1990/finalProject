"""
All utilities for ctr
"""


from math import radians, cos, sin, asin, sqrt,atan,atan2,degrees,ceil
from scipy.spatial import distance_matrix
from sklearn.cluster import DBSCAN
import cv2

import constants as const
import arrange
from classes import *

def solidity (cnt):
    """
    Returns contour solidity
    """
    area = cv2.contourArea(cnt)
    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    solidity = float(area)/hull_area
    return solidity

def moving_av (lst,param):
    """
    returns moving average of list as a list in the same length
    
    """
    p = int((param - 1) / 2)
    paded = [0]* p + lst + [0] * p
    mv = []
    for i in range(p):
        s = sum(lst[:(param-p+i)])
        n = param - p + i
        mv.append (s/n)
    for i in range (p,len(lst)-p):
        s = sum(lst[i-p:i+p+1])
        mv.append(s/param)
    for i in range (len(lst)-p,len(lst)):
        s = sum(lst[i-p:])
        n = p + len(lst) - i
        mv.append(s/n)
    return mv

def add_tuple (t1,t2):
    """
    Return sum of tuple (a,b) + (c,d) = (a+c,b+d)
    """
    return (t1[0] + t2[0],t1[1] + t2[1])

def todecimal(coords):
    """Calculate decimal values for geo coordinates
    """
    return (coords[0][0]+ #deg
            coords[1][0]/(coords[1][1]*60)+ #minutes
            coords[2][0]/(coords[2][1]*3600))# seconds

def reject_outliers (data):
    """
    """
    data = np.array(data)
    m = 1.5
    return data[abs(data - np.mean(data)) < m * np.std(data)]
    
def divide(img ,dim , overlap):
    """
    divied
    """
    tiles = []
    height , width = img.shape[0:2]
    n_width = ceil((width-overlap)/(dim-overlap))
    n_height = ceil((height-overlap)/(dim-overlap))
    last_tile_width = width - (dim + (n_width - 2) * (dim - overlap)) + overlap
    last_tile_height = height - (dim + (n_height - 2) * (dim - overlap)) + overlap
    for line in range(n_height - 1):
        ypos = line * (dim - overlap)
        dims = (dim,dim)
        for column in range(n_width - 1):
            mat_position = (line,column)
            xpos = column * (dim - overlap)
            xy_pos = (xpos,ypos)
            tiles.append(Tile(xy_pos , mat_position,dims))
        #last col tile
        mat_position = (line,column + 1)
        xpos += (dim - overlap)
        xy_pos = (xpos,ypos)
        dims = (last_tile_width , dim)
        tiles.append(Tile(xy_pos , mat_position,dims))
    #last row tiles
    ypos += (dim - overlap)
    dims = (dim , last_tile_height)
    line += 1
    for column in range(n_width - 1):
        mat_position = (line, column)
        xpos = column * (dim - overlap)
        xy_pos = (xpos,ypos)
        tiles.append(Tile(xy_pos , mat_position,dims))
    #last col tile
    mat_position = (line,column + 1)
    xpos += (dim - overlap)
    xy_pos = (xpos,ypos)
    dims = (last_tile_width , last_tile_height)
    tiles.append(Tile(xy_pos , mat_position,dims))
    return tiles
    
def add_offset (conts,offset):
    """
    """
    for c in conts:
        for p in c:
            p[0][0] += offset[0]
            p[0][1] += offset[1]
    return conts
    
def paint_large_conts (img,conts,size,color=(0,0,0)):
    """
    """
    for c in conts:
        if cv2.contourArea(c) > size: #check!!!!
            cv2.drawContours(img,[c],0,color,-1)
    return img
    
def find_green_contoures (image,conts):
    """
    """
    img = image.get_image()
    img = paint_large_conts (img,conts,size = 500000)
    #gray-scale,blur,binary and contour find       
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(5,5),5)
    ret,thresh = cv2.threshold(gray,1,255,cv2.THRESH_BINARY)
    _, contours,_ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)#*********change 2nd parameter******************
    #clean_noise
    green_conts = []
    for c in contours:
        if (len(c) > 100):
            green_conts.append(c)
    return green_conts
    
def spot_black(spot,black_ratio=0.3):
    """
    """
    h,w = spot.shape[:2]
    if ((h == 0) or (w == 0)): #edge of image - disregard
        return True
    pix_num = spot.shape[0] * spot.shape[1]
    bc = np.bincount(np.ravel(spot))
    blacks = bc[0]
    all = sum(bc)
    return ((blacks/all) > black_ratio)
    
def spot_g_b_ratio (spot,brown_val=127,black_ratio = 0.7):
    """
    """
    pix_num = spot.shape[0] * spot.shape[1]
    flat = np.ravel(spot)
    bc = np.bincount(flat)
    if (bc[0]/pix_num > black_ratio):
        return const.BLACK
    if (len(bc) < brown_val): #no browns or greens
        return const.BLACK
    browns = max(bc[brown_val],1) #avoid dividing by zero
    
    blacks = bc[0] 
    if (len(bc) > 254):
        greens = bc[-1]
        if greens/browns > 9:
            return const.GREEN
        elif greens/browns > 4:
            return const.YELLOW
        else:
            return const.RED
    else : #no greens, 'many' browns
        return const.RED

def tree_list (conts,hier,ind):
    """
    Lists all indexes of a contour and its descendants
    Args:
        - conts - list of all contours
        - hier - heirarchy array
        - ind - index of the contour (to list the descendants)
    Returns:
        - list of all indexes of the descendants
    """
    fc = hier[ind][const.FIRST_CHILD] #first child index
    if ( fc == -1): #no child
        # print ('leaf')
        return [ind]
    else:#there are children.send all recursively to func 
        l = [ind]
        nc = fc
        while not (nc == -1): #there are 'brothers'
            l.extend (tree_list(conts,hier,nc))
            nc = hier[nc][const.NEXT]
        return l
  
def weight_area (area):
    if area < const.MAX_LEAF_AREA:
        return 1
    elif area < const.BIG_LEAF_AREA:
        return 2
    elif area < const.FEW_LEAVES_AREA:
        return 5
    else:
        return 10
     
def find_DBSCAN_labels (centers,weights):
    """
    """
    dist_mat = distance_matrix(centers,centers)
    db = DBSCAN(eps =const.DBSCAN_EPS, min_samples = 10).fit(dist_mat,
                                        sample_weight=weights)
    return (db.labels_)
    
def divide_and_find_clusters (sils):
    """
    """
    clusters = []
    if len(sils) > const.MAX_CLUSTER_SIZE:
        lst = divide2cluster(sils)
    else:
        lst = [sils]
    for l in lst:
        clusters.extend(find_browns_clusters(l))
    return clusters
    
def find_browns_clusters (sils):
    """
    Find clusters of silhouettes. Uses DBSCAN algorithm.
    weights are normalized  area of the contour:
        -
        -
        -
        -
        -
    Args:
        sils - a silhouettes list
    Returns:
        clusters list 
    """ 
    if (len(sils) == 0):
        return []
    weights = [weight_area(s.area) for s in sils]
    centers = [(s.center.x,s.center.y) for s in sils]
    conts = [s.cont for s in sils]
    labels = find_DBSCAN_labels (centers,weights)
    n_clusters = max(labels)+1
    clusters = []
    #for each label/group create cluster, determine type,get contour
    for i in range (n_clusters):
        same_label_conts = [conts[j] for j in range(len(conts))
                            if (labels[j] == i)]
        same_label_sils = [sils[j] for j in range(len(sils))
                            if (labels[j] == i)]
        type_val = sum([s.area*s.type for s in same_label_sils]) / sum([s.area for s in same_label_sils])
        if (type_val > (const.TARGET + const.BARE_SOIL) / 2):
            type = const.TARGET
        else:
            type = const.BARE_SOIL
            
        cnt = np.vstack(same_label_conts)
        # hull = cv2.convexHull(points.tolist())
        hull = cv2.convexHull(cnt)

        clusters.append((hull,type))
    return clusters

def pxl2xy (pxl,wd):
    """
    Translates pxl position on image to xy utm coordinates
    """
    xpos,ypos = pxl.x,pxl.y 
    xcoor = wd['topleftx'] + xpos*wd['xscale']
    ycoor = wd['toplefty'] + ypos*wd['yscale']
    return Point(xcoor,ycoor)
    
def xy2pxl (xy_pt,wd):
    """
    Translates xy utm coordinates to pxl position on image 
    """
    xcoor = xy_pt.x
    ycoor = xy_pt.y
    xpos = int((xcoor - wd['topleftx'])/wd['xscale'])
    ypos = int((ycoor - wd['toplefty'])/wd['yscale'])
    return Point(xpos,ypos)
    
def rect_val(x,y,msize,rect):
    x_min = max (0,x-rect)
    y_min = max (0,y-rect)
    x_max = min (msize[0],x+rect)
    y_max = min (msize[1],y+rect)
    return (x_min,x_max,y_min,y_max)

def close_tile (location,wd,images,locmat,rect=20):
    mat,xmin,ymax = locmat
    x = int(location.x - xmin)
    if (x < 0): x = 0
    if (x > len(locmat[0][1])) : x = len(locmat[0][1])
    y = int(ymax - location.y)
    x_min,x_max,y_min,y_max = rect_val(y,x,mat.shape,rect)
    cropped = mat[x_min:x_max,y_min:y_max]
    ims_in_rect = mat[np.nonzero(mat)].astype(int)
    closest = images[ims_in_rect[0]]
    for ind in ims_in_rect[1:]:
        im = images[ind-1]
        if (location.distance(im.center) < 
            location.distance(closest.center)):
            closest = im
    return (closest)
    
def split_l(lst,on_x):
    if (on_x):
        xs = [i.center.x for i in lst]
        mid_x = (max(xs) + min(xs))/2
        lst_1 = []
        lst_2 = []
        for l in lst:
            if l.center.x > mid_x:
                lst_2.append(l)
            else:
                lst_1.append(l)
        return [lst_1,lst_2]
    else:
        ys = [i.center.y for i in lst]
        mid_y = (max(ys) + min(ys))/2
        lst_1 = []
        lst_2 = []
        for l in lst:
            if l.center.y > mid_y:
                lst_2.append(l)
            else:
                lst_1.append(l)
        return (lst_1,lst_2)

def divide2cluster(lst,on_x=True):
    """
    Splits list l into several lists, all shorter than MAX_CLUSTER
    """
    if len(lst) < const.MAX_CLUSTER_SIZE :
        if ((len(lst)) == 0):
            return lst
        return [lst]
    else:
        lst1,lst2 = split_l(lst,on_x)
        return (divide2cluster(lst1,not(on_x)) + 
                divide2cluster(lst2,not(on_x))) 

def inside_box(p,center,w,h):
    """
    checks if p inside box of center and h,w sizes
    """
    return((abs(p.x - center.x) < w/2) and 
           (abs(p.y - center.y) < h/2))
                
def check_clusters_match (s1,s2,psize):
    """
    """
    w1,h1 = s1.b_rect[2:] # size of bounding rectangle
    w2,h2 = s2.b_rect[2:]
    
    w1 *= psize
    w2 *= psize
    h1 *= psize
    h2 *= psize
    
    if((inside_box(s1.xy_center,s2.xy_center,w2,h2)) or
       (inside_box(s1.xy_center,s2.xy_center,w2,h2))): # one contains the other
        if (s1.area > s2.area):
            return const.FIRST
        else:
            return const.SECOND
    if (s1.xy_center.distance(s2.xy_center) > const.DIS_TOLERANCE): # outside tolerance
        return const.NO_MATCH
    if ((abs(1 - s1.area / s2.area) < const.AREA_DELTA) and # similar dimentions
       (abs(1 - h1 / h2) < const.DIMS_DELTA) and (abs(1 - w1 / w2) < const.DIMS_DELTA)):
        if (s1.area > s2.area):
            return const.FIRST
        else:
            return const.SECOND
    return const.NO_MATCH
    
                
def join_clusters_by_location (im1,im2):
    """
    """
    clus1 = im1.clusters
    clus2 = im2.clusters
    psize = (im1.pxl_size + im2.pxl_size) / 2
    deleted1 = []
    deleted2 = []
    if ((len(clus1) == 0) or (len(clus2) == 0)):
        return
    for i,c1 in enumerate(clus1):
        for j,c2 in enumerate(clus2):
            match = check_clusters_match (c1,c2,psize)
            if (match == const.FIRST): #c2 in c1
                deleted2.append(j)
            elif (match == const.SECOND): #c1 is in c2
                b = True
                deleted1.append(i)
                break
            #else: do nothing
    im1.clusters = [clus1[i] for i in range(len(clus1)) if 
            not i in deleted1]
    im2.clusters = [clus2[i] for i in range(len(clus2)) if 
            not i in deleted2]
            
def join_clusters (images,routes,locmat):
    """
    """
    ts = time.time()
    r = int(ceil(images[0].pxl_size * (sqrt(images[0].dimentions[0]**2 + 
                                images[0].dimentions[1]**2))))
    print ('Joining clusters...')
    for i,im in enumerate(images):
        
        neighbours_ind = arrange.neighbours(i,locmat,r)
        neighbours = [images[i] for i in neighbours_ind]
        for neighbour in neighbours:
            join_clusters_by_location (im,neighbour)
            # shift = arrange.find_shift (im,neighbour,routes)
            # join_image_clusters (im,neighbour,shift)
    te = time.time()
    print ('Done in {} seconds'.format(te-ts))
# def sils_intersection (first,second):
    # """
    # finds intersection between 2 silhouettes
    # """
            
def valid_shift (pt,dim):
    return ((0 <= pt.x <= dim[0]) and (0 <= pt.y <= dim[1]))
    
def join_image_clusters (im1,im2,shift):
    """
    """
    clusters1 = im1.clusters
    clusters2 = im2.clusters
    remove1 = []
    remove2 = []
    xmax,ymax = im1.dimentions
    imcenter = Point(xmax/2,ymax/2)
    for c1 in clusters1:
        p = add_tuple ((c1.center.x,c1.center.y),shift)
        shifted_center = Point(p[0],p[1])
        if valid_shift(shifted_center,im1.dimentions):
            for c2 in clusters2:
                if (shifted_center.distance(c2.center) < 
                        const.MAX_JOINED_CLUSTERS_DISTANCE):
                    # take closest to center
                    if c1.center.distance(imcenter) < c2.center.distance(imcenter):
                        remove2.append(c2)
                    else:
                        remove1.append(c1)
    for c in remove1:
        im1.clusters.remove(c)
    for c in remove2:
        im2.clusters.remove(c)
            
def eq_histogram(img):
    """
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    channel_l = lab[...,0]
    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(20,20))
    cl = clahe.apply(channel_l)
    lab[...,0] = cl
    bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return (bgr)
    
def heat_map (pano,wd,sils,sqr_size):
    """
    Args:
        pano image
        wd - world orientation of pano (keys = ['xscale','rotationy',
        'rotationx','yscale','topleftx','toplefty']
        sils - Silhouettes list
        sqr_size: in meters
    Returns:
        an heat map image of pano
    """
    minx = wd['topleftx']
    maxy = wd['toplefty']
    pxl_size = int(sqr_size/wd['xscale']) #assuming xscale = yscale!!!
    #set initial green overlay
    overlay = np.zeros_like(pano)
    overlay[:,:] = const.GREEN
    #build a dictionary of contours in sqr_size

    loc_dict = {}
    for i,s in enumerate(sils):
        x = int(round((s.xy_center.x-minx)/sqr_size))
        y = int(round((maxy-s.xy_center.y)/sqr_size))
        k = str(x) + '.' + str(y)
        v = i
        if (k in loc_dict):
            loc_dict[k].append(i)
        else:
            loc_dict[k] = [i]
    #build locations matrix
    # x_val = wd['xscale']*pano.shape[1]/sqr_size
    # y_val = wd['yscale']*pano.shape[0]sqr_size
    # x_size = 
    # loc_mat = np.zeros((y_val+1,x_val+1))
    #set values in loc matrix according to sils dict
    for k in loc_dict.keys():
        t_area = sum([sils[i].true_area for i in loc_dict[k]])
        coverage = t_area / np.square(sqr_size)
        pos = k.split('.')
        x = int(pos[0]) * sqr_size
        y = int(pos[1]) * sqr_size
        px,py = xy2pxl(Point(minx+x,maxy-y),wd).p_tuple()
        if (coverage > const.BAD_COVERAGE):
            color = const.RED
            cv2.rectangle(overlay,(px,py),(px+pxl_size,py+pxl_size),color,
                                thickness=-1)
        elif (coverage > const.MEDIUM_COVERAGE):
            color = const.YELLOW
            cv2.rectangle(overlay,(px,py),(px+pxl_size,py+pxl_size),color,
                    thickness=-1)
    img = np.copy(pano)    
    res = cv2.addWeighted(img,0.5,overlay,0.5,0)
    mypath = 'C:\\Users\\eran\\mystuff\\imageproc\\code\\sandbox\\output\\'
    cv2.imwrite(mypath+'heatmap1.jpg',res) 
    res2 = np.copy(res)
    conts = [s.cont for s in sils]
    # cv2.drawContours (res2,conts,-1,(0,0,0),2)
    # ax = plt.subplot (121)
    # ax.imshow (res2[...,::-1])
    # plt.title ('heatmap')

    # plt.subplot (122,sharex = ax,sharey = ax)
    # plt.imshow (img[...,::-1])
    # plt.title ('org')

    
    # plt.show()
    return res
    
      
def heat_maps (image,all_sil,hs_size = 200):
    """
    """
    img = image.get_image()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    overlay = np.zeros_like(img)
    conts = [s.cont for s in all_sil]

    #find greens
    green_conts = find_green_contoures(image,conts)
    cv2.drawContours (img,green_conts,-1,(0,0,0),5)
    #paints greens in white,sick areas in gray,other in black
    paint_large_conts (gray,green_conts,1,color=255)
    paint_large_conts (gray,conts,1,127)
    paint_large_conts (gray,conts,500000,0)
    #plt.imshow(gray),plt.show()
    maxX,maxY = img.shape[:2]
    for g in green_conts:
        X,Y,W,H = cv2.boundingRect(g)
        h_spots = int (H/hs_size)
        if not(H%hs_size):#there is no residue
            h_spots -= 1
        if h_spots < 1 : h_spots = 1
        w_spots = int (W/hs_size)
        if not(W%hs_size):#there is residue
            w_spots -= 1
        if w_spots < 1 : w_spots = 1
        for h in range (h_spots):
            x = X+h*hs_size
            for w in range (w_spots):
                y = Y+w*hs_size
                if (x+hs_size < maxX) and (y+hs_size < maxY):
                    spot = gray[x:(x+hs_size),y:(y+hs_size)]
                    color = spot_g_b_ratio(spot)
                    # if (val < 0): #black spot
                        # color = (0,0,0)
                    # elif val > .95:
                        # color = (0,255,0)
                    # elif g2b > .7:
                        # color = (0,255,255)
                    # else:
                        # color = (0,0,255)
                    if not(sum(color) == 0):
                        cv2.rectangle(overlay,(y,x),(y+hs_size,x+hs_size),color,
                                thickness=-1) 
    res = cv2.addWeighted(img,0.5,overlay,0.5,0)
    mypath = 'C:\\Users\\eran\\mystuff\\imageproc\\code\\sandbox\\output\\'
    cv2.imwrite(mypath+'heatmap1.jpg',res)    
    cv2.drawContours (res,green_conts,-1,(0,0,0),5)
    ax = plt.subplot (121)
    ax.imshow (img[...,::-1])
    plt.title ('gray map')

    plt.subplot (122,sharex = ax,sharey = ax)
    plt.imshow (res[...,::-1])
    plt.title ('rects')

    
    plt.show()

def pano_stats (dim,scale,art, bare_soil,target,blacks):
    """
    Calc statistic of panorama image
    """
    
    stats = {}
    stats['total_pic_area'] = dim[0] * dim[1] * scale**2
    stats['total_field_area'] = stats['total_pic_area'] - blacks * scale**2
    stats['art_glades_area'] = sum([s.area for s in art]) * scale**2
    stats['bare_soil_area'] = sum([s.area for s in bare_soil]) * scale**2
    stats['targets_area'] = sum([s.area for s in target]) * scale**2
    stats['total_growth_area'] = stats['total_field_area'] - stats['art_glades_area'] - stats['bare_soil_area'] - stats['targets_area']
    stats ['anomaly_ratio'] = (stats['targets_area'] + 
            stats['bare_soil_area']) / stats['total_growth_area']
    
    print (stats)
    return stats
    
    
    
    