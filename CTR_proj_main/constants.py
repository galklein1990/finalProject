"""
all constants in cotton target recognition
"""

#program modes
ORTHO = 1
ONE_PLAIN_IMAGE = 2
RAW_IMAGES = 3
IMAGES_AND_ORTHO = 4

TILE_SIZE = 2000
#silhouette modes:
ARTIFICIAL = 1
BARE_SOIL = 2
TARGET = 3
OTHER = 4

MAX_CLUSTER_SIZE = 1000 #num of elements to cluster from

MAX_SHOW_DIM = 10000 # other wise resize image
MIN_LEAF_AREA = 100e-4 #min contour. 100 sqr cm
MAX_ARTIFICIAL_TRUE_SIZE = 20 #sqr meters
MIN_ARTIFICIAL_SOLIDITY = 0.5
#arrange contstants
DIRECTION_ACCURACY = 10 #accuracy of course directions in degrees
MIN_IMAGES_IN_ROUTE = 2
OPPOSIT_ROUTES_PARAM = 30 #determing if a route is opposite
#stitching

#homography matrix sanity
HOMOGRAPHY_DIAGONAL = (0.95,1.05)
MAX_NUMERATOR_COEF = 0.09
MAX_DENUM_COEF = 0.0001

NUM_OF_MATCHES = 20 #matches in BRISK matches
BATCH_SIZE = 5 #num of route images to stitch
PICS_IN_TILE = 5

SCALE_FACTOR = 1/10 #scale images before matching

MAX_JOINED_CLUSTERS_DISTANCE = 100

DBSCAN_EPS = 1500

DIS_TOLERANCE = 3
# joining clusters
FIRST = 1
SECOND = 2
NO_MATCH = 0

AREA_DELTA = 0.2
DIMS_DELTA = 0.2                  
MOVING_AVERAGE_PARAM = 5

OVERLAP_RATIO = 0.8

#join clusters criteria
CENTER_SIL_DISTANCES = 2 #meters
SIMILAR_AREA = 0.25

#tiles divide
TILE_DIM = 1000
TILE_OVERLAP = 250

#contours hierarchy
NEXT = 0
PREVIOUS = 1
FIRST_CHILD = 2
PARENT = 3

#heat map
BAD_COVERAGE = 0.8
MEDIUM_COVERAGE = 0.4
RED_PER = 60
YELLOW_PER = 30
GREEN_PER = 10
BLACK_COLOR = (0,0,0)
RED = (0,0,255)
GREEN = (0,255,0)
YELLOW = (0,255,255) 

#brown regions clustering
MAX_LEAF_AREA = 5000
BIG_LEAF_AREA = 10000
FEW_LEAVES_AREA = 15000