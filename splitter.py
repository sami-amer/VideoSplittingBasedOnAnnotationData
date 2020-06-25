 import os
import subprocess
import time
import copy
import statistics
import random
import pandas as pd

MAIN_VID_PATH = '/Volumes/Wellness/Wellness/'
MAIN_ANN_PATH = '/Users/sharifa/wellness/annotation/'
MAIN_OUT_VID_PATH = '/Users/sharifa/wellness/videos/'
FOLDER_CHAR = '/' #'\\' for windows
FFMPEG_COMMAND = 'ffmpeg' # "F:\\Work\\Extras\\ffmpeg\\bin\\ffmpeg.exe" for windows


def import_data(file_name, videopath=None):
    """
    This is the main function to import duration data.  
    
    Cycles through a text file and saves start times and duration in key and dictionary, respectively

    arguments:
        file_name (str): path to the text file
        videopath (str): defaults to None, in which the function get_p_s is used. Otherwise uses the passed in videopath

    returns:
        Attention, Behavior, Emotion (dict): Dictionaries where keys correspond to tags and values to lists of tuples that contain duration data
    """
    annotation_data = pd.read_csv(file_name,'\t',header=None, usecols=[0,5, 2,4]).set_index([0,5])
    try:
        annotation_data = annotation_data.drop(index='default',level=0)
    except:
        pass
    
    #label Level
    annotation_label = annotation_data.index.unique(1).to_list()
    # print(annotation_label)
    annotation_label = ['off-tsak', 'on-task', 'distarcted', 'focused', 'idle', 'Bored', 'Satisfied', 'Confused']
    annotation_Dict = {elem: pd.DataFrame for elem in annotation_label}
    for label in range(len(annotation_label)):
        label_name = annotation_label[label]
        this_label_data = [[]]
        try:
            this_label_data = annotation_data.xs(label_name,level=1).to_numpy()
        except:
            pass
        annotation_Dict[label_name] = this_label_data

    return annotation_Dict

def import_paths_from_txt(txt):
    """
    borrowed from data counter, imports lines as elements of a list.

    allows us to store paths in persistent .txt file, and just pull from that

    arguments:
        txt (str): path to text file with paths

    returns:
        out (list): list where elements are paths
    """
    
    out = pd.read_csv(txt,header=None).values.flatten().tolist()
    return out

def split_and_save(rootdir, orig, start, duration, name):
    """
    runs command line commands to navigate to the given directory and use FFMPEG to clip a video

    arguments:
        rootdir (str): the directory to navigate to, usually whatever allows us to access the video in the 'orig' variable
        orig (str): full path or name of the video to copy from
        start (int/float): start time of clip, in seconds
        duration (int/float): duration of clip, in seconds
        name (str): full path or name of video to be saved

    returns:
        nothing, but the command it runs will create a new video wherever 'name' is, depending on where the function navigated with using 'rootdir'
    """
    # os.chdir(rootdir)
    subprocess.run(
        [
            FFMPEG_COMMAND,  ## make this point to where ffmpeg is, or if FFMPEG is in PATH then just replace this with FFMPEG
            "-i",
            orig,
            "-ss",
            start,
            "-t",
            duration,
            # "-c:v",  ## signifies that we are rencoding video
            #"h264_nvenc",  ## if there is no nvidia GPU, replace this with the CPU Powered 'libx264' (compared to a 1660Super, the difference using time.perfcounter is 1 to 16)
            # "-qp",
            # "16",  ## higher means less quality and lower file size. inverse is true
            rootdir+name
        ]
    )

def getVideoPath(textPath, locations):
    file_name_splits = os.path.basename(textPath).split('.')[0].split('_')
    p = file_name_splits[0]
    s = file_name_splits[1]
    csv = pd.read_csv(locations, header=None, usecols=[0,1,2]).set_index([0,1])
    vid_folder = csv.xs([p,s]).to_list()[0]
    full_path = MAIN_VID_PATH + p + FOLDER_CHAR + s + FOLDER_CHAR + vid_folder
    found = False
    for file in os.listdir(full_path):
        if file.endswith(".mp4") and file.startswith(p + '_' + s):
            path = os.path.join(full_path, file)
            found = True
            return path ## this is not complete because it requires the program to be in the right directory.  This should be alleviated with the 'rootdir' variable in other functions

    if not found:
        print('Video file does not exsist')
        return ''
        # raise Exception('Video file does not exsist')

def split_random(tier, tag, counter, rootdir, directory, duration):
    print(tier[tag])
    choice = random.choice(tier[tag])
    print(choice)
    if len(choice)==0:
        print('this file has no annotion of '+tag)
        return ''
    
    tag = tag.replace('-', '_')
    name = tag + "_" + str(counter) + '.mp4'
    split_and_save(rootdir, directory, str(choice[0]), str(duration), name)
    return name

if __name__ == "__main__":
    paths = import_paths_from_txt("pathsTotal.txt")
    passes = 100
    counter = 0
    random_paths = random.choices(paths, k=passes)
    
    for path in random_paths:
        counter += 1
        print(path)
        vPath = getVideoPath(path, "all_filesFeb27.csv")
        if not vPath:
            continue
        annotations_dict = import_data(MAIN_ANN_PATH+path, vPath)
        # get_random_clips(annotations_dict,'on-task',MAIN_OUT_VID_PATH,vPath,1,counter)
        split_random(annotations_dict, 'off-tsak', counter, MAIN_OUT_VID_PATH+'1s_off_task/', vPath, 1)
        # split_random(annotations_dict, 'on-tsak', counter, MAIN_OUT_VID_PATH+'2s_on_task/', vPath, 2)
        # split_random(annotations_dict, 'off-tsak', counter, MAIN_OUT_VID_PATH+'2s_off_task/', vPath, 2)

