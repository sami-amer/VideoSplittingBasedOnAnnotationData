import pandas as pd
import numpy as np
from interval import interval

MAIN_ANN_PATH = '/home/sami/Work/resources/inter-rater/'#/Users/sharifa/wellness/annotation/'
FOLDER_CHAR = '/' #'\\' for windows

annotation_label = ['on-task', 'off-tsak', 'Satisfied', 'Confused', 'Bored', 'focused', 'idle', 'distarcted']


def get_Individual_statistics(annotation_data, seconds):
	# label Level
	annotation_label = annotation_data.index.unique(1).to_list()
	print(annotation_label)
	# annotation_label = ['off-tsak', 'on-task', 'distarcted', 'focused', 'idle', 'Bored', 'Satisfied', 'Confused']
	# print(annotation_label)
	for label in range(len(annotation_label)):
		label_name = annotation_label[label]
		print('*--*--*--*  *--*--*--*  *--*--*--*  *--*--*--*  *--*--*--*')
		print(label_name)
		try:
			print('*--*--*--*  all  *--*--*--*')
			print(annotation_data.xs(label_name, level=1).describe())
			
			print('*--*--*--*  exculde ' + str(seconds) +' seconds  *--*--*--*')
			exculde_1s_subset = annotation_data.loc[annotation_data[4] >= seconds]
			print(exculde_1s_subset.xs(label_name, level=1).describe())
			
			print('*--*--*--*  only ' + str(seconds) +' seconds *--*--*--*')
			a_1s_subset = annotation_data.loc[annotation_data[4] < seconds]
			print(a_1s_subset.xs(label_name, level=1).describe())
			
		except:
			print('Issues with lable '+str(label_name))
			pass

def get_raw_split_annotations(this_annotation_data, seconds):
	start_time = 0
	end_time = this_annotation_data[3].describe().max()
	
	index = np.vstack([np.array(range(start_time, int(end_time), int(seconds))), np.array(range(start_time+seconds, int(end_time+seconds), int(seconds)))])
	split_annotations = pd.DataFrame(index=list(index), columns=annotation_label)
	split_intervals = [interval(x) for x in index.T]
	
	for label in range(len(annotation_label)):
		label_name = annotation_label[label]
		try:
			annotation_start_end_times = np.delete(this_annotation_data.xs(label_name, level=1).values, 2 , axis=1)
			lables_intervals = interval.union([interval(x) for x in annotation_start_end_times])
			found_within = [each_interval in lables_intervals for each_interval in split_intervals]
			split_annotations[label_name] = found_within
			
		except:
			# print('Issues with lable ' + str(label_name))
			pass
	
	# no lables from the same tire should be TRUE at the same time - sanity check
	# print('sanity check')
	x= split_annotations[(split_annotations['off-tsak'] == True) & (split_annotations['on-task']== True) ]
	if len(x) > 0:
		print('Issues with off-tsak - on-task')
		print(x)
	x= split_annotations[(split_annotations['distarcted'] == True) & (split_annotations['focused']== True)  & (split_annotations['idle']== True)]
	if len(x) > 0:
		print('Issues with  distarcted, focused, idle')
		print(x)
	x= split_annotations[(split_annotations['Bored'] == True) & (split_annotations['Satisfied']== True)  & (split_annotations['Confused']== True)]
	if len(x) > 0:
		print('Issues with  Bored, Satisfied, Confused')
		print(x)
	
	return split_annotations

def get_association(all_assosiations, assosiations_keys, seconds):
	all_assosiations = all_assosiations.fillna(0)
	overall_assosiations_temp = all_assosiations.reset_index(drop=True).set_index(annotation_label)
	overall_assosiations_temp['segments'] = 1
	overall_assosiations = overall_assosiations_temp.groupby(by=annotation_label).sum()
	assosiations_keys.update(overall_assosiations)
	print('*--*--*--*  *--*--*--*  *--*--*--*  *--*--*--*  *--*--*--*')
	print(assosiations_keys)
	print('*--*--*--*  *--*--*--*  *--*--*--*  *--*--*--*  *--*--*--*')
	print('Total segemnts for ',seconds,' seconds: ',assosiations_keys.sum())


if __name__ == "__main__":
	seconds = 5
	
	paths = pd.read_csv("pathsTotal.txt",header=None).values.flatten().tolist()
	counter=0
	
	# # prepfare association keys dataframe
	assosiations_keys = pd.read_csv('assocaition_categories.csv', sep='\t', header=None,
	                                   names=annotation_label).set_index(annotation_label)
	assosiations_keys['segments'] = 0
	
	#merge all annotaion files in a big dataframe for statistics
	for path in paths:
		counter+=1
		# print(path)
		this_annotation_data = pd.read_csv(MAIN_ANN_PATH + path, '\t', header=None, usecols=[0, 5, 2, 3, 4]).set_index([0, 5])
		
		try:
			this_annotation_data = this_annotation_data.drop(index='default', level=0)
		except:
			pass
		

		#analyze each file association
		#TODO: no percentage implemnted yet
		# print(this_annotation_data)
		this_split_annotations = get_raw_split_annotations(this_annotation_data, seconds)
		#TODO: do we need to save this into files?

		if counter==1:
			annotation_data = this_annotation_data
			all_assosiations = this_split_annotations
		else:
			annotation_data = annotation_data.append(this_annotation_data)
			all_assosiations = all_assosiations.append(this_split_annotations)
	# print(annotation_data.describe())
	# get_Individual_statistics(annotation_data,seconds)

	# now we have a dataframe with all lables and intervals, we should calcualte the associations
	get_association(all_assosiations, assosiations_keys, seconds)
	
	
	
	
	
	

