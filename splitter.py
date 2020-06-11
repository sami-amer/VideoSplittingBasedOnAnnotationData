import os
import subprocess
import time
# os.chdir('/Users/samiatmit/Documents/School_Files/Spring_2020/UROP/VidSplit/')
# preNat = time.perf_counter()
# subprocess.call(['ffmpeg', '-i', 'P01_S02.mp4', '-ss', '90', '-t', '60', '-c:v', 'copy', 'Video/testNormal.mp4'])
# postNat = time.perf_counter()
# subprocess.call(['ffmpeg', '-i', 'P01_S02.mp4', '-ss', '90', '-t', '60', '-c:v', 'libx264', '-qp', '16', 'Video/testEncoded.mp4'])
# postEnc = time.perf_counter()
# print(postNat - preNat)
# print(postEnc - postNat)

def import_data(file_name):

    distarcted, idle, Satisfied, on_task, off_tsak, Bored, Confused, focused = [],[],[],[],[],[],[],[]
    with open(file_name, "r") as f:
        for line in f:
            line = line.split("\t")
            del line[1]
            line[-1] = line[-1].strip("\n")
            if line[1] == 'default':
                continue
            else:
                if (line[4] != 'on-task') and (line[4] != 'off-tsak'):
                    locals()[line[4]].append((line[1],line[3]))
                elif line[4] == 'on-task':
                    on_task.append((line[1],line[3]))
                elif line[4] == 'off-tsak':
                    off_tsak.append((line[1],line[3]))
                else:
                    print ('unkown error')
    Attention = {'distracted': distarcted, 'idle': idle, 'focused':focused}
    Behavior = {'off-task': off_tsak,'on-task' : on_task}
    Emotion = {'bored': Bored, 'confused' : Confused, 'satisfied': Satisfied}
    return Attention, Behavior, Emotion

def split_and_save(rootdir, name, start, duration, orig):
    os.chdir(rootdir)
    subprocess.call(['ffmpeg', '-i', orig, '-ss', start, '-t', duration, '-c:v', 'libx264', '-qp', '16', name])


def split_vids(Attention, Behavior, Emotion, rootdir, orig):
    counter = 0
    for tup in Attention['distracted']:
        counter += 1
        name = '/Users/samiatmit/Documents/School_Files/Spring_2020/UROP/VidSplit/ExampleOut/Attention/distracted/a_D_' + str(counter) + '.mp4'
        split_and_save(rootdir,orig,tup[0],tup[1],name)
if __name__ == "__main__":
    A,B,E = import_data('ExtractedP01_S02_Irene.txt')
    split_vids(A,B,E,'/Users/samiatmit/Documents/School_Files/Spring_2020/UROP/VidSplit/','/Video/P01_S02.mp4')