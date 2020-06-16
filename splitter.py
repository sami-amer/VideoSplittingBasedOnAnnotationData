import os
import subprocess
import time
import copy
import statistics

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
    merges two dictionaires into one, CURRENTLY ONLY WORKS WITH LISTS. requires deep copy module
    """
    output = copy.deepcopy(dic1)
    for key in dic2.keys():
        if key in output:
            output[key].extend(dic2[key])
        else:
            output[key] = dic2[key]
    return output


def get_p_s(path, nameOnly = False): ## NOTE: This may need to be edited
    pathR = path[::-1]
    for index,char in enumerate(pathR):
        if char == '\\':
            num = len(path) - index
            videopath = path[num:]
            videopath = videopath[:7]
            if nameOnly:
                break
            videopath = "F:\\Work\\VidSplit\\Video\\" + videopath[:3] + '\\' + videopath[4:8] + "\\" + videopath +".mp4" # just change this line to make it point to video path
            break
    
    return videopath   


def import_data(file_name):

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
                    print('unknown error with line: ' + str(line))
    
    Attention = {"distracted": distarcted, "idle": idle, "focused": focused}
    Behavior = {"off-task": off_tsak, "on-task": on_task}
    Emotion = {"bored": Bored, "confused": Confused, "satisfied": Satisfied}
    return Attention, Behavior, Emotion


def import_data_multiple(filelist):
    A, B, E = import_data(filelist[0])
    for f in filelist[1:]:
        x, y, z = import_data(f)
        A = merge_dics(A, x)
        B = merge_dics(B, y)
        E = merge_dics(E, z)
    return A, B, E


def import_paths_from_txt(txt):
    out = []
    with open(txt, "r") as file:
        for line in file:
            line = line.strip("\n")
            out.append(line)
    return out


def split_and_save(rootdir, name, start, duration, orig):
    os.chdir(rootdir)
    subprocess.run(
        [
            "F:\\Work\\Extras\\ffmpeg\\bin\\ffmpeg.exe",
            "-i",
            orig,
            "-ss",
            start,
            "-t",
            duration,
            "-c:v",
            "h264_nvenc",
            "-qp",
            "16",
            name,
        ]
    )


## TODO: os.mkdir to make the directories before beggining to split files

## TODO: implement function for random choices
## TODO: implement as in task instructions

def make_dirs(root):
    os.chdir(root)
    os.mkdir() ## TODO: make this make the proper directories for saving

def split_vids(Attention, Behavior, Emotion, rootdir, override = 0):
    counter = 0
    for tup in Attention["distracted"]:
        counter+=1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Attention\\distracted\\a_D_"
            + videoName
            + ".mp4"
        )  
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:
            split_and_save(
                rootdir, name, tup[1], tup[2], tup[0]
            )  ## tup[0] so that multiple files can be used at once


    for tup in Attention["idle"]:
        counter+=1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Attention\\idle\\a_I_"
            + videoName
            + ".mp4"
        ) 
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:            
            split_and_save(
                rootdir, name, tup[1], tup[2], tup[0]
            )  ## tup[0] so that multiple files can be used at once

    for tup in Attention["focused"]:
        counter += 1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Attention\\focused\\a_F"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:
            split_and_save(rootdir, name, tup[1], tup[2],tup[0])

    for tup in Behavior["on-task"]:
        counter+=1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Behavior\\on-task\\b_N_"
            + videoName
            + ".mp4"
        )  
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:
            split_and_save(
                rootdir, name, tup[1], tup[2], tup[0]
            )  ## tup[0] so that multiple files can be used at once

    for tup in Behavior['off-task']:
        counter+=1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name =(
            "F:\\Work\\VidSplit\\ExampleOut\\Behavior\\off-task\\b_F"
            + videoName
            +".mp4"
        )
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:
            split_and_save(
                rootdir, name, tup[1], tup[2], tup[0]
            )
    
    for tup in Emotion['satisfied']:
        counter += 1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name =(
            "F:\\Work\\VidSplit\\ExampleOut\\Emotion\\satisfied\\e_S"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:
            split_and_save(
                rootdir,name,tup[1],tup[2],tup[0]
            )
    for tup in Emotion['confused']:
        counter += 1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name =(
            "F:\\Work\\VidSplit\\ExampleOut\\Emotion\\confused\\e_C"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:
            split_and_save(
                rootdir,name,tup[1],tup[2],tup[0])
    for tup in Emotion['bored']:
        counter += 1
        videoName = get_p_s(tup[0], True) + '_' + str(counter)
        name =(
            "F:\\Work\\VidSplit\\ExampleOut\\Emotion\\bored\\e_B"
            + videoName
            + ".mp4"
        )
        if override > 0:
            split_and_save(
                rootdir, name, tup[1], override, tup[0]
            )
        else:
            split_and_save(
                rootdir,name,tup[1],tup[2],tup[0])

def get_durations(a, b, e):
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
    ## TODO: cycle through tuple and pull durations into their respective dictionaries.  run functionless to get tallies
    for tup in a['distracted']:
        Attention['distracted'].append(float(tup[2]))
    for tup in a['idle']:
        Attention['idle'].append(float(tup[2]))
    for tup in a['focused']:
        Attention['focused'].append(float(tup[2]))
    for tup in b['off-task']:
        Behavior['off-task'].append(float(tup[2]))
    for tup in b['on-task']:
        Behavior['on-task'].append(float(tup[2]))
    for tup in e['bored']:
        Emotion['bored'].append(float(tup[2]))
    for tup in e['confused']:
        Emotion['confused'].append(float(tup[2]))
    for tup in e['satisfied']:
        Emotion['satisfied'].append(float(tup[2]))

    return Attention, Behavior, Emotion


if __name__ == "__main__":
    # A,B,E = import_data('ExtractedP01_S02_Irene.txt')
    # split_vids(A,B,E,'F:\\Work\\VidSplit\\','F:\\Work\\VidSplit\\Video\\P01_S02.mp4')
    # d1 = {"a": [1, 2, 3], "b": [1, 2, 3], "d": [1, 2, 3, 4, 5, 6],'e':[1,2,3,4,5,6]}
    # d2 = {"a": [3, 4, 5], "b": [3, 4, 5], "c": [1, 2, 3, 4, 5],'e':[]}
    # d3 = merge_dics(d1,d2)
    # print(d3)
    paths = import_paths_from_txt("paths.txt")
    a, b, e = import_data_multiple(paths)
    split_vids(a,b,e, 'F:\\Work\\VidSplit\\') 
    # ad,bd,ed = get_durations(a,b,e)
    # lessThan = 0
    # moreThan = 0 ## if a clip == 1, it is counted as less than
    # withoutList = []
    # allList = []
    # for duration in ad['distracted']:
    #     if duration > 1.0:
    #         moreThan += 1
    #         withoutList.append(duration)
    #         allList.append(duration)
    #     elif duration <= 1.0:
    #         lessThan += 1
    #         allList.append(duration)
    #     else:
    #         print('unknown error with: ' + str(duration))
    # withoutAvg = statistics.mean(withoutList)
    # allAvg = statistics.mean(allList)
    # withoutMed = statistics.median(withoutList)
    # allMed = statistics.median(allList)
    # maximum = max(allList)
    # withoutMin = min(withoutList)
    # allMin = min(allList)
    
    # print(
    #     "# less than 1s: " + str(lessThan) + '\n' +
    #     "# more than 1s: " + str(moreThan) + '\n' +
    #     'Avg Duration w/o less than 1s: ' + str(withoutAvg) + '\n' +
    #     "Avg Duration with less than 1s: " + str(allAvg) + '\n' +
    #     "Median Duration w/o less than 1s: " + str(withoutMed) + '\n' +
    #     "Median duration with less than 1s: " + str(allMed) + '\n' +
    #     "Max Duration: " + str(maximum) + '\n' +
    #     "Minimum w/o less than 1s: " + str(withoutMin) + '\n'+
    #     "Minimum with less than 1s: " + str(allMin) + '\n' 
    # )
    