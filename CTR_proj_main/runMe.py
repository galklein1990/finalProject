import CTR_main1 as main
import sys

def initPath(ortho,ortho_data,pickle_file,image_path,output):
    paths ={}
    paths['ortho'] = ortho.replace("'", '')
    paths['ortho_data'] = ortho_data.replace("'", '')
    paths['pickle_file'] = pickle_file.replace("'", '')
    paths['image_path'] = image_path.replace("'", '')
    paths['output'] = output.replace("'", '')
    return paths
def run(mode ,ortho,ortho_data,pickle_file,image_path,output):
    paths = initPath(ortho,ortho_data,pickle_file,image_path,output);
    main.main_flow(mode, paths)


if __name__ == '__main__':
    run(sys.argv[1][1:-1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])

# python runMe.py 'ortho+images' 'C:/Users/mdwq87/Downloads/project/resizedOrtho.tif' 'C:/Users/mdwq87/Downloads/project/resized.tfw' '
# ' 'C:/Users/mdwq87/Downloads/project/input' 'C:/Users/mdwq87/Downloads/project/output'