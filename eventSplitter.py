import pandas as pd
import random
import time
import os
import subprocess

MAIN_VID_PATH = 'Video/'
MAIN_ANN_PATH = '/home/sami/Work/resources/inter-rater/'
MAIN_OUT_VID_PATH = 'ExampleOut/'
FOLDER_CHAR = '/'
FFMPEG_COMMAND = 'ffmpeg'
ALL_FILES_CSV = 'all_filesFeb27.csv'
CODEC = "h264_nvenc" ## if there is no nvidia GPU, replace this with the CPU Powered 'libx264'

def get_end_time(file_input): ## TODO: make cleaner, comment **DONE**
    '''
    gets the max time of a video file, so tha the import_duration_ms can creat template columns to be filled

    arguments:
        file_input(str): path to the file input, usually an annotation .txt
    '''
    data = pd.read_csv(file_input,'\t',header=None, usecols=[0,5, 2,3]).set_index([0,5])
    end_time = data[3].describe().max()
    return end_time

def split_and_save(rootdir, orig, start, duration, name): ## TODO: make cleaner **DONE**
    """
    runs command line commands to FFMPEG to clip a video

    arguments:
        rootdir (str): the directory to navigate to, usually whatever allows us to access the video in the 'orig' variable
        orig (str): full path or name of the video to copy from
        start (int/float): start time of clip, in seconds
        duration (int/float): duration of clip, in seconds
        name (str): full path or name of video to be saved

    returns:
        nothing, but the command it runs will create a new video wherever 'name' is, depending on where the function navigated with using 'rootdir'
    """
    subprocess.run(
        [
            FFMPEG_COMMAND,  ## make this point to where ffmpeg is, or if FFMPEG is in PATH then just replace this with FFMPEG
            "-i",
            orig,
            "-ss",
            start,
            "-t",
            duration,
            "-c:v",  ## signifies that we are rencoding video
            CODEC,
            "-qp",
            "16",  ## higher means less quality and lower file size. inverse is true
            rootdir+name
        ]
    )

def import_data_durations(file_name): ## TODO: make cleaner, fix doc strings **DONE**
    """
    This is the main function to import duration data.  
    
    Cycles through a text file and saves start times and duration in key and dictionary, respectively

    arguments:
        file_name (str): path to the text file

    returns:
        annotation_data (df): a data frame indexed by type of engagment, which contains start and duration stats
    """
    annotation_data = pd.read_csv(file_name,'\t',header=None, usecols=[0,5, 2,4]).set_index([0,5])
    try:
        annotation_data = annotation_data.drop(index='default',level=0)
    except:
        pass
    
    return annotation_data

def import_paths_from_txt(txt): ## TODO: make cleaner, fix doc strings **DONE**
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

def clean_cuts(ms_data, window,kind): ## NOTE: brand new, merging of two functions
    '''
    merge of clean_cuts_percentages and clean_cuts_status.  Output is changed between the two using the 'kind' string

    arguments:
        ms_data (df): data from import_data_ms
        window (int): size of the calculation window, in milliseconds
        kind (str): '%' if you want percentages, 'bool' if you want status (True/False)
    '''
    previndex = 0
    output = pd.DataFrame(columns = ['sequence','on-task', 'off-task', 'satisfied', 'confused', 'bored', 'focused','idle','distracted']).set_index('sequence')
    seq = 0 
    for i in range(len(ms_data) + 1):
        if i == 0:
            continue
        if i % window == 0:
            seq += 1
            if kind == '%':
                data = get_percentages(ms_data,window, previndex,i)
            elif kind == 'bool':
                data = get_status(ms_data, window, previndex, i) 
            previndex = i
            output.loc[seq] = data.loc[0].tolist()
    return output


def import_data_ms(file_name): # TODO: make this use data frames
    endtime = get_end_time(file_name)
    Behavioral_Engagement = [0] * int(endtime * 1000)
    Attention_Engagement = [0] * int(endtime * 1000)
    Emotional_Engagement = [0] * int(endtime * 1000)
    annotation_data = import_data_durations(file_name)
    tags = ['on-task','off-tsak','Bored','Confused','Satisfied','distarcted','idle','focused']
    labeled = {'behavior':Behavioral_Engagement,'attention':Attention_Engagement, 'emotion': Emotional_Engagement}
    behaviorTags = {'on-task','off-tsak'}
    attentionTags = {'distarcted', 'idle', 'focused'}
    emotionTags = {'Bored', 'Confused','Satisfied'}
    ms_data = pd.DataFrame.from_dict(labeled)
    for tag in tags:
        try:
            times = annotation_data.xs(tag,level=1).iterrows()
        except:
            continue
        for elem in times:
            start = int(1000 * (elem[1][2]))
            stop = int(1000 * (start + elem[1][4]) + 1)
            if tag == 'off-tsak' or tag == 'Bored' or tag == 'distarcted':
                val = 1
            elif tag == 'on-task' or tag == 'Confused' or tag == 'idle':
                val = 2
            elif tag == 'Satisfied' or tag == 'focused':
                val = 3
            if tag in behaviorTags:
                label = 'behavior'
            elif tag in attentionTags:
                label = 'attention'
            elif tag in emotionTags:
                label = 'emotion'
            # print(tag)
            ms_data.loc[start:stop,label] = val

    return ms_data

def get_percentages(df, window,previndex,i): ## TODO: make cleaner and comment **DONE**
    '''
    used in clean_cuts to get percentages per window.

    arguments:
        all arguments are inherited from clean_cuts
    '''
    behaviorCounts = df[previndex:i]['behavior'].value_counts()
    attentionCounts = df[previndex:i]['attention'].value_counts()
    emotionCounts = df[previndex:i]['emotion'].value_counts()
    percentageDF = pd.DataFrame(columns=['on-task','off-task','satisfied','confused','bored','focused','idle','distracted'])
    percentageDF.loc[0] = [0,0,0,0,0,0,0,0]
    for item in behaviorCounts.iteritems():
        if item[0] == 1:
            percentageDF.loc[0]['off-task'] = item[1]/ window
        elif item[0] == 2:
            percentageDF.loc[0]['on-task'] = item[1]/ window 
    for item in attentionCounts.iteritems():
        if item[0] == 1:
            percentageDF.loc[0]['distracted'] = item[1]/ window
        elif item[0] == 2:
            percentageDF.loc[0]['idle'] = item[1]/ window
        elif item[0] == 3:
            percentageDF.loc[0]['focused'] = item[1]/ window          
    for item in emotionCounts.iteritems():
        if item[0] == 1:
            percentageDF.loc[0]['bored'] = item[1]/ window
        elif item[0] == 2:
            percentageDF.loc[0]['confused'] = item[1]/ window
        elif item[0] == 3:
            percentageDF.loc[0]['satisfied'] = item[1]/ window  
    
    return percentageDF

def get_status(df, window,previndex,i):
    '''
    used in clean_cuts to get percentages per window.

    arguments:
        all arguments are inherited from clean_cuts
    '''
    behaviorCounts = df[previndex:i]['behavior'].value_counts()
    attentionCounts = df[previndex:i]['attention'].value_counts()
    emotionCounts = df[previndex:i]['emotion'].value_counts()
    statusDF = pd.DataFrame(columns=['on-task','off-task','satisfied','confused','bored','focused','idle','distracted'])
    statusDF.loc[0] = [False,False,False,False,False,False,False,False]
    for item in behaviorCounts.iteritems():
        if item[0] == 1:
            statusDF.loc[0]['off-task'] = True
        elif item[0] == 2:
            statusDF.loc[0]['on-task'] = True 
    for item in attentionCounts.iteritems():
        if item[0] == 1:
            statusDF.loc[0]['distracted'] = True
        elif item[0] == 2:
            statusDF.loc[0]['idle'] = True
        elif item[0] == 3:
            statusDF.loc[0]['focused'] = True          
    for item in emotionCounts.iteritems():
        if item[0] == 1:
            statusDF.loc[0]['bored'] = True
        elif item[0] == 2:
            statusDF.loc[0]['confused'] = True
        elif item[0] == 3:
            statusDF.loc[0]['satisfied'] = True 
    return statusDF

def getVideoPath(textPath, locations, extras = False):
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
            if extras:
                return path, p, s ## this is not complete because it requires the program to be in the right directory.  This should be alleviated with the 'rootdir' variable in other functions
            return path
    if not found:
        print('Video file does not exsist')
        return ''
        # raise Exception('Video file does not exsist')

def event_splitter(path,data, window):
    tags = ['on-task','off-tsak','Bored','Confused','Satisfied','distarcted','idle','focused']
    vPath, p, s = getVideoPath(path, ALL_FILES_CSV,True)
    for tag in tags:
        try:
            times = data.xs(tag,level=1).iterrows()
        except:
            continue
        for elem in times:
            if len(elem) > 1:
                start = elem[1][2] - window
                if start < 0:
                    start = 0
                duration = elem[1][4]
                eventDuration = window*2
                if start == 0:
                    eventDuration = window
                if duration < window:
                    name = p + '_' + s + '_' + 'event' + '_' + tag + '_B' +str(round(start,3)) + '_' + str(window) + 'sINCOMPLETE.mp4' # the name has INCOMPLETE because the tag is shorter than the desired window for the event                    
                    split_and_save(MAIN_OUT_VID_PATH,vPath,str(start),str(eventDuration),name)
                else:
                    name = p + '_' + s + '_' + 'event' + '_' + tag + '_B' +str(round(start,3)) + '_' + str(window) + 's.mp4'
                    split_and_save(MAIN_OUT_VID_PATH,vPath,str(start),str(eventDuration),name)
                    #TODO add a line here that links to a non-event splitter
                    non_event_splitter(start,duration,window,p,s,tag,vPath,'I')

def non_event_splitter(start,duration,window,p,s,tag,vPath,char):
    start = start + window
    duration = duration - window
    iterations = (int(duration) // window) + 1
    for i in range(iterations):
        name = p + '_' + s + '_' + 'non-event' + '_' + tag + '_S' +str(round(start,3)) + '_' +char+ str(i+1) +'_' +str(window) + 's.mp4'
        if i == (iterations - 1):
            split_and_save(MAIN_OUT_VID_PATH,vPath,str(start),str(duration - (window * (iterations-1))),name)
            break
        split_and_save(MAIN_OUT_VID_PATH,vPath,str(start),str(window),name)
        start = start + window

def association_durations(segments):
    # KEY: 
    #   NSF :: On task, Satisfied, Focused
    #   FSF :: Off task, Satisfied, Focused
    #   FBI :: Off Task, Bored, Idle
    #   FBD :: Off Task, Bored, Distracted
    associationTimes = {'NSF':[],'FSF':[],'FBI':[],'FBD':[]}
    # vPath,p, s = getVideoPath(path, ALL_FILES_CSV, True)
    continue1,continue2,continue3,continue4 = False,False,False,False
    for index,row in segments.iterrows():
        onTask = row['on-task']
        offTask = row['off-task']
        satisfied = row['satisfied']
        focused = row['focused']
        bored = row['bored']
        idle = row['idle']
        distracted = row['distracted']
        if continue1:
            if [onTask, satisfied, focused] == [True, True, True]:
                continue
            else:
                associationTimes['NSF'].append((startSecond,index))
                continue1 = False
        
        if continue2:
            if [offTask, satisfied, focused] == [True, True, True]:
                continue
            else:
                associationTimes['FSF'].append((startSecond,index))
                continue2 = False
        
        if continue3:
            if [offTask, bored, idle] == [True, True, True]:
                continue
            else:
                associationTimes['FBI'].append((startSecond,index))
                continue3 = False
        
        if continue4:
            if [offTask, bored, distracted] == [True, True, True]:
                continue
            else:
                associationTimes['FBD'].append((startSecond,index))
                continue4 = False

        if [onTask, satisfied, focused] == [True, True, True]:
            startSecond = index
            continue1 = True
            continue
        
        if [offTask, satisfied, focused] == [True, True, True]:
            startSecond = index
            continue2 = True
            continue

        if [offTask, bored, idle] == [True, True, True]:
            startSecond = index
            continue3 = True
            continue
        
        if [offTask,bored,distracted] == [True, True, True]:
            startSecond = index
            continue4 = True
            continue
    return associationTimes

def associaton_non_event_splitter(path,window):
    vPath, p, s = getVideoPath(path, ALL_FILES_CSV, True)
    data = import_data_ms(path)
    maxLen = (len(data)/1000)
    segments = clean_cuts_status(data,1000)
    durations = association_durations(segments)
    for duration in durations['NSF']:
        if duration[0] > (maxLen - window):
            continue
        if duration[1] < window:
            continue
        if duration[0] < window:
            start = window
        start = duration[1]
        if duration[1] > (maxLen - window):
            duration = maxLen - window
        duration = duration[1]
        non_event_splitter(start,duration,window,p,s,'on-task_satisfied_focused',vPath,'E')

    for duration in durations['FSF']:
        if duration[0] > (maxLen - window):
            continue
        if duration[1] < window:
            continue
        if duration[0] < window:
            start = window
        start = duration[1]
        if duration[1] > (maxLen - window):
            duration = maxLen - window
        duration = duration[1]
        non_event_splitter(start,duration,window,p,s,'off-task_satisfied_focused',vPath,'E')

    for duration in durations['FBI']:
        if duration[0] > (maxLen - window):
            continue
        if duration[1] < window:
            continue
        if duration[0] < window:
            start = window
        start = duration[1]
        if duration[1] > (maxLen - window):
            duration = maxLen - window
        duration = duration[1]
        non_event_splitter(start,duration,window,p,s,'off-task_bored_idle',vPath,'E')

    for duration in durations['FBD']:
        if duration[0] > (maxLen - window):
            continue
        if duration[1] < window:
            continue
        if duration[0] < window:
            start = window
        start = duration[1]
        if duration[1] > (maxLen - window):
            duration = maxLen - window
        duration = duration[1]
        non_event_splitter(start,duration,window,p,s,'off-task_bored_distracted',vPath,'E')
        
if __name__ == "__main__":
    paths = import_paths_from_txt("paths.txt")
    passes = 100
    random_paths = random.choices(paths, k=passes)
    data = import_data_ms(MAIN_ANN_PATH + paths[1]) # this data is a dictionary where keys are tags and values are arrays
    # onTask = data.xs('on-task',level = 1)
    # for elem in data.xs('on-task',level = 1).iterrows():
    #     print(len(elem)) # [1][2] is start, [1][4] is duration
    cuts = (clean_cuts(data,1000,'bool'))
    print(cuts)
    # for i,row in cuts.iterrows():
    #     print(row['on-task'])
    # print(data)
    # path= paths[1]
    # event_splitter(MAIN_ANN_PATH + path,data,3)
    # for path in random_paths:
    #     data = import_data_ms(path)
    #     cuts = clean_cuts_status(data,1000)
    #     print(association_durations(cuts))

    # associaton_non_event_splitter(paths[1],3)