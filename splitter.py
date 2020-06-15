import os
import subprocess
import time
import copy

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
        for line in f:
            line = line.split("\t")
            del line[1]
            line[-1] = line[-1].strip("\n")
            if line[1] == "default":
                continue
            else: ## TODO: Continue if else statements
                if line[4] == 'distarcted':
                    distarcted.append((file_name,line[1], line[3])) 
                elif line[4] == 'idle':
                    idle.append((file_name,line[1],line[3]))
                elif line[4] == 'Satisfied':
                    Satisfied.append((file_name,line[1],line[3]))
                elif line[4] == 'Bored':
                    Bored.append((file_name,line[1], line[3]))
                elif line[4] == 'Confused':
                    Confused.append((file_name,line[1], line[3]))
                elif line[4] == 'focused':
                    focused.append((file_name,line[1],line[3]))
                elif line[4] == "on-task":
                    on_task.append((file_name,line[1], line[3]))
                elif line[4] == "off-tsak":
                    off_tsak.append((file_name, line[1], line[3]))
                else:
                    print("unknown error")
    Attention = {"distracted": distarcted, "idle": idle, "focused": focused}
    Behavior = {"off-task": off_tsak, "on-task": on_task}
    Emotion = {"bored": Bored, "confused": Confused, "satisfied": Satisfied}
    return Attention, Behavior, Emotion


def import_data_multiple(filelist):
    A, B, E = import_data(filelist[0])
    for f in filelist[1:]:
        x,y,z = import_data(f)
        A = merge_dics(A, x)
        B = merge_dics(B,y)
        E = merge_dics(E, z)
    return A, B, E


def import_paths_from_txt(txt):
    out = []
    with open(txt,'r') as file:
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
            "libx264",
            "-qp",
            "16",
            name,
        ]
    )


## TODO: os.mkdir to make the directories before beggining to split files
## TODO: Decide how to split all files, how to organize them etc.
## TODO: implement duration override

def split_vids(Attention, Behavior, Emotion, rootdir):
    counter = 0
    for tup in Attention["distracted"]:
        counter += 1
        name = (
            "F:\\Work\\VidSplit\\ExampleOut\\Attention\\distracted\\a_D_"
            + str(counter)
            + ".mp4"
        ) ## TODO: find a way to change name based on original file

        split_and_save(rootdir, name, tup[1], tup[2], tup[0]) ## tup[0] so that multiple files can be used at once


if __name__ == "__main__":
    # A,B,E = import_data('ExtractedP01_S02_Irene.txt')
    # split_vids(A,B,E,'F:\\Work\\VidSplit\\','F:\\Work\\VidSplit\\Video\\P01_S02.mp4')
    # d1 = {"a": [1, 2, 3], "b": [1, 2, 3], "d": [1, 2, 3, 4, 5, 6],'e':[1,2,3,4,5,6]}
    # d2 = {"a": [3, 4, 5], "b": [3, 4, 5], "c": [1, 2, 3, 4, 5],'e':[]}
    # d3 = merge_dics(d1,d2)
    # print(d3)
    paths = import_paths_from_txt('paths.txt')
    a,b,e = import_data_multiple(paths)
    print(a)