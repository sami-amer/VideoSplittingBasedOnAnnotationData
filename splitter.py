import os
import subprocess
import time
import copy
import statistics
import random
import pandas as pd

# os.chdir('F:\\Work\\VidSplit')
# print(os.getcwd())
# preNat = time.perf_counter()
# subprocess.run(['F:\\Work\\Extras\\ffmpeg\\bin\\ffmpeg.exe', '-i', 'Video\\P01_S02.mp4', '-ss', '90', '-t', '60', '-c:v', 'copy', 'Video\\testNormal.mp4'])
# postNat = time.perf_counter()
# subprocess.call(['F:\\Work\\Extras\\ffmpeg\\bin\\ffmpeg.exe', '-i', 'Video\\P01_S02.mp4', '-ss', '90', '-t', '60', '-c:v', 'nvenc', '-qp', '8', 'Video\\testEncoded.mp4'])
# postEnc = time.perf_counter()
# print(postNat - preNat)
# print(postEnc - postNat)


def merge_dics(dic1, dic2):
    """
    takes two dictionaries that have the same keys and extends the lists that are attached to those keys

    arguments:
        dic1, dic2 (dict): python dictionaries that you want to merge

    returns:
        output(dict): the merged dictionary
    """
    output = copy.deepcopy(dic1)
    for key in dic2.keys():
        if key in output:
            output[key].extend(dic2[key])
        else:
            output[key] = dic2[key]
    return output


def get_p_s(path, nameOnly=False):  ## NOTE: This may need to be edited
    """
    **NOTE** this is deprecated with the new method that pulls from the csv, and is mostly used with nameOnly == True
    
    Takes a path to an annotation text file and gets the video path 

    arguments:
        path (str): the path of the annotation textfile
        nameOnly (bool): FALSE by default.  When true it doesn't return a full path but just the name

    returns:
        videopath (str): a string representing either the path or name
    """
    pathR = path[::-1]
    for index, char in enumerate(pathR):
        if char == "\\":
            num = len(path) - index
            videopath = path[num:]
            videopath = videopath[:7]
            if nameOnly:
                break
            videopath = (
                "F:\\Work\\VidSplit\\Video\\"
                + videopath[:3]
                + "\\"
                + videopath[4:8]
                + "\\"
                + videopath
                + ".mp4"
            )  # just change this line to make it point to video path
            break

    return videopath


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
    distarcted, idle, Satisfied, on_task, off_tsak, Bored, Confused, focused = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    with open(file_name, "r") as f:
        if videopath is None:
            videopath = get_p_s(file_name)
        for line in f:
            line = line.split("\t")
            del line[1]
            line[-1] = line[-1].strip("\n")
            if line[0] == "default":
                continue
            else:
                if line[4] == "distarcted":
                    distarcted.append((videopath, line[1], line[3]))
                elif line[4] == "idle":
                    idle.append((videopath, line[1], line[3]))
                elif line[4] == "Satisfied":
                    Satisfied.append((videopath, line[1], line[3]))
                elif line[4] == "Bored":
                    Bored.append((videopath, line[1], line[3]))
                elif line[4] == "Confused":
                    Confused.append((videopath, line[1], line[3]))
                elif line[4] == "focused":
                    focused.append((videopath, line[1], line[3]))
                elif line[4] == "on-task":
                    on_task.append((videopath, line[1], line[3]))
                elif line[4] == "off-tsak":
                    off_tsak.append((videopath, line[1], line[3]))
                else:
                    print("unknown error with line: " + str(line))

    Attention = {"distracted": distarcted, "idle": idle, "focused": focused}
    Behavior = {"off-task": off_tsak, "on-task": on_task}
    Emotion = {"bored": Bored, "confused": Confused, "satisfied": Satisfied}
    return Attention, Behavior, Emotion


def import_data_multiple(filelist):
    """
    makes it possible to use import data on a list of files as opposed to one file

    arguments:
        filelist (list): a list of strings that can be used by `import_data`

    returns:
        A, B, E (dict): larger versions of the dictionaries returns by `import_data`
    """
    A, B, E = import_data(filelist[0])
    for f in filelist[1:]:
        x, y, z = import_data(f)
        A = merge_dics(A, x)
        B = merge_dics(B, y)
        E = merge_dics(E, z)
    return A, B, E


def import_paths_from_txt(txt):
    """
    borrowed from data counter, imports lines as elements of a list.

    allows us to store paths in persistent .txt file, and just pull from that

    arguments:
        txt (str): path to text file with paths

    returns:
        out (list): list where elements are paths
    """
    out = []
    with open(txt, "r") as file:
        for line in file:
            line = line.strip("\n")
            out.append(line)
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
    os.chdir(rootdir)
    subprocess.run(
        [
            "F:\\Work\\Extras\\ffmpeg\\bin\\ffmpeg.exe",  ## make this point to where ffmpeg is, or if FFMPEG is in PATH then just replace this with FFMPEG
            "-i",
            orig,
            "-ss",
            start,
            "-t",
            duration,
            "-c:v",  ## signifies that we are rencoding video
            "h264_nvenc",  ## if there is no nvidia GPU, replace this with the CPU Powered 'libx264' (compared to a 1660Super, the difference using time.perfcounter is 1 to 16)
            "-qp",
            "16",  ## higher means less quality and lower file size. inverse is true
            name
        ]
    )


## TODO: os.mkdir to make the directories before beggining to split files

## TODO: implement function for random choices
## TODO: implement as in task instructions


def make_dirs(root):
    """
    NOTE NOT CURRENTLY DONE
    """
    os.chdir(root)
    os.mkdir()  ## TODO: make this make the proper directories for saving


def split_vids(Attention, Behavior, Emotion, rootdir, override = 0):
    """
    **NOTE** as of right now, directories must be made by hand before running this function
    
    splits a video based on ALL tags.

    arguments:
        Attention, Behavior, Emotion (dict): dictonaries mapping tags to lists of duration tuples, like the output of `import_data`
        rootdir (str): path to navigate to for `split_and_save` function
        override (int/float): defaults to 0 and is ignored.  if present, forces all clips to be this length in seconds

    returns:
        nothing, but the commands being run on the command line creates videos

    """
    counter = 0  # this is simply used to add a number to avoid duplicate names and to see if something was skipped
    for tup in Attention["distracted"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Attention\\distracted\\a_D_"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)

    counter = 0
    for tup in Attention["idle"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Attention\\idle\\a_I_" + videoName + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)

    counter = 0
    for tup in Attention["focused"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Attention\\focused\\a_F"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)

    counter = 0
    for tup in Behavior["on-task"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Behavior\\on-task\\b_N_"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)

    counter = 0
    for tup in Behavior["off-task"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Behavior\\off-task\\b_F"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)

    counter = 0
    for tup in Emotion["satisfied"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Emotion\\satisfied\\e_S"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)

    counter = 0
    for tup in Emotion["confused"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Emotion\\confused\\e_C"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)

    counter = 0
    for tup in Emotion["bored"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + "_" + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Emotion\\bored\\e_B" + videoName + ".mp4"
        )
        if override > 0:
            split_and_save(rootdir, tup[0], tup[1], override, name)
        else:
            split_and_save(rootdir, tup[0], tup[1], tup[2], name)


## TODO: make directory a variable


def get_durations(a, b, e):
    """
    takes the dictionaries and creates a copy that ONLY has duarations. Used in statistical analysis of durations

    arguments:
        a, b, e (dict): dictionaries mapping tags to duration tuples, like the outputs of `import_data`

    returns:
        Attentions, Behavior, Emotion (dict): similiar dictionaries as inputs except it only has durations

    """
    ## NOTE: Duration is the third element of the tuple
    distarcted, idle, Satisfied, on_task, off_tsak, Bored, Confused, focused = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    Attention = {"distracted": distarcted, "idle": idle, "focused": focused}
    Behavior = {"off-task": off_tsak, "on-task": on_task}
    Emotion = {"bored": Bored, "confused": Confused, "satisfied": Satisfied}
    for tup in a["distracted"]:
        Attention["distracted"].append(float(tup[2]))
    for tup in a["idle"]:
        Attention["idle"].append(float(tup[2]))
    for tup in a["focused"]:
        Attention["focused"].append(float(tup[2]))
    for tup in b["off-task"]:
        Behavior["off-task"].append(float(tup[2]))
    for tup in b["on-task"]:
        Behavior["on-task"].append(float(tup[2]))
    for tup in e["bored"]:
        Emotion["bored"].append(float(tup[2]))
    for tup in e["confused"]:
        Emotion["confused"].append(float(tup[2]))
    for tup in e["satisfied"]:
        Emotion["satisfied"].append(float(tup[2]))

    return Attention, Behavior, Emotion


def sleeperFunc(a, b, e):
    """
    Not a real function, jsut here so it can be collapsed and doesnt clutter my __main__

    used to get stats of durations
    """

    ad, bd, ed = get_durations(a, b, e)
    lessThan = 0
    moreThan = 0  ## if a clip == 1, it is counted as less than
    withoutList = []
    allList = []
    for duration in ad["distracted"]:
        if duration > 1.0:
            moreThan += 1
            withoutList.append(duration)
            allList.append(duration)
        elif duration <= 1.0:
            lessThan += 1
            allList.append(duration)
        else:
            print("unknown error with: " + str(duration))
    withoutAvg = statistics.mean(withoutList)
    allAvg = statistics.mean(allList)
    withoutMed = statistics.median(withoutList)
    allMed = statistics.median(allList)
    maximum = max(allList)
    withoutMin = min(withoutList)
    allMin = min(allList)

    print(
        "# less than 1s: "
        + str(lessThan)
        + "\n"
        + "# more than 1s: "
        + str(moreThan)
        + "\n"
        + "Avg Duration w/o less than 1s: "
        + str(withoutAvg)
        + "\n"
        + "Avg Duration with less than 1s: "
        + str(allAvg)
        + "\n"
        + "Median Duration w/o less than 1s: "
        + str(withoutMed)
        + "\n"
        + "Median duration with less than 1s: "
        + str(allMed)
        + "\n"
        + "Max Duration: "
        + str(maximum)
        + "\n"
        + "Minimum w/o less than 1s: "
        + str(withoutMin)
        + "\n"
        + "Minimum with less than 1s: "
        + str(allMin)
        + "\n"
    )


def getVideoPath(textPath, locations):
    """
    gets the video path based on a csv with all paths

    arguments:
        textPath (str): the path in text form so that identifiers can be pulled from it
        locations (str): path to the csv in which the first four rows comprise the path

    returns:
        path (str): a partial path that is complete if in the right directory
    """
    identifiers = get_p_s(textPath, True)
    p = identifiers[:3]
    s = identifiers[4:]
    csv = pd.read_csv(locations, header=None)
    for r, val in enumerate(csv[0]):
        if val == p and csv[1][r] == s:
            row = r
            break
    path = (
        str(csv[0][row]) + "\\" + str(csv[1][row]) + "\\" + str(csv[2][row]) + "\\" + str(csv[3][row])
    )  ## Slashes need to be adjusted for Mac/Linux
    return path ## this is not complete because it requires the program to be in the right directory.  This should be alleviated with the 'rootdir' variable in other functions

def split_random(tier, tag, counter, rootdir, directory, duration):
    """
    gets a clip of set duration randomly

    arguments:
        tier (dict): the dictionary mapping tags to lists of duration tuples
        tag (str): the tag you want the videos to be associated with
        counter (int): passed through to avoid naming conflicts
        rootdir (str): the directory for the terminal to point to
        directory (str): path to original video file
        duration (int/float): duration of the clip
    
    returns:
        name (str): the path to the newly split video, so it can be merged later

    """
    if tier[tag]:
        choice = random.choice(tier[tag])
    else:
        return None
    if tag == 'on-task':
        tag = 'on_task'
    elif tag == 'off-task':
        tag = 'off_task'
    name = tag + "_" + str(counter) + '.mp4'
    split_and_save(rootdir, directory, str(choice[1]), str(duration), name)
    return name

def merge_vids(rootdir,pathsFile,output):
    """
    uses ffmpeg to merge videos based on a text file with paths

    arguments:
        rootdir (str): the directory where the program must run
        pathsFile (str): path to the text file that contains VALID FILES.  The one in the repository can be used 'pathsTotal.txt' 
        output (str): path/name of the output file, must end in .mp4 (or other compatible formats)

    returns:
        Nothing, but the commands create a video file
    """
    os.chdir(rootdir)
    subprocess.run(
        [
            "F:\\Work\\Extras\\ffmpeg\\bin\\ffmpeg.exe",
            "-safe",
            "0",
            "-f",
            "concat",
            "-i",
            pathsFile,
            "-c", ## if you would like to re encode instead, which creates smaller file sizes, change this to "-c:v"
            "copy", ## and change this to the codec, namely libx264 for CPU and h264_nvenc for Nvidia GPU
            output
        ]
    )

def get_random_clips(tier,tag, rootdir,directory,duration,passes, output):
    """
    puts together multiple functions to comprehensivley generate random clips tied to a tag

    arguments:
        tier (dict): the dictionary mapping tags to lists of duration tuples
        tag (str): the tag you want the videos to be associated with
        rootdir (str): the directory for the terminal to point to
        directory (str): path to original video file
        duration (int/float): duration of the clip
        passes (int): the number of times to pull a random clip
        output (str): name/path of output file
    
    returns:
        Nothing, but the commands create a video file
    
    """
    counter = 0
    paths = []
    for r in range(passes):
        counter += 1
        path = split_random(tier,tag,counter,rootdir,directory,duration)
        paths.append(path)
    with open('toMerge.txt','w+') as f:
        for path in paths: 
            f.write("file " + path + '\n')
    merge_vids(rootdir, 'toMerge.txt', output)
    for path in paths:
        os.remove(path)

def clip_generator(pathsFile, locationsFile,tag, rootdir,duration,passes,output):
    """
    This is what should be used to achieve the goal set out in Task 1 Goal 1
    
    arguments:
        pathsFile (str): path to the text file that contains VALID FILES.  The one in the repository can be used 'pathsTotal.txt'    
        locationsFile (str): path to the csv in which the first four rows comprise the path
        tag (str): the tag you want the videos to be associated with
        rootdir (str): the directory for the terminal to point to
        duration (int/float): duration of the clip
        passes (int): the number of times to pull a random clip
        output (str): name/path of output file

    returns:
        Nothing, but the commands create a video file
    
    """
    paths = import_paths_from_txt(pathsFile)
    path = random.choice(paths)
    vPath = getVideoPath(path,locationsFile)
    A,B,E = import_data(path,vPath)
    if tag == 'on-task' or tag == 'off-task':
        tier = B
    elif tag =='focused' or tag == 'idle' or tag == 'distracted':
        tier = A
    elif tag == 'satisfied' or tag == 'confused' or tag == 'bored':
        tier = E
    get_random_clips(tier,tag,rootdir,vPath,duration,passes,output)

if __name__ == "__main__":
    # paths = import_paths_from_txt("paths.txt")
    # path = random.choice(paths) # this file can be pulled from the repo, is not dependant on system due to the way the path is cut down
    # vPath = getVideoPath(path, "all_filesFeb27.csv")
    # A,B,E = import_data(path, vPath)
    # get_random_clips(B,'on-task',"F:\\Work\\VidSplit\\ExampleOut",vPath,1,60)
    clip_generator("paths.txt","all_filesFeb27.csv",'off-task',"F:\\Work\\VidSplit\\ExampleOut",1.5,60,"off_task_clipped.mp4")
