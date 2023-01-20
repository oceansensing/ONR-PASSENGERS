import pandas as pd
import numpy as np
import xarray as xr
import datetime
import os
import glob
import csv

def find_wav_file(dir_path, gli_date, gli_time):
    # Use the glob.glob() method to get a list of file names in the directory
    file_paths = glob.glob(os.path.join(dir_path,'*.wav'))
    file_names = [os.path.basename(file_path) for file_path in file_paths]

    # Use a list comprehension to extract the numeric part of each file name for date
    date = [int(file.split('T')[0]) for file in file_names]
    date_sorted = np.sort(date)

    # Use searchsorted function to find max date
    max_date = date_sorted[np.searchsorted(date_sorted, gli_date, side='right')-1]

    #create new list times only on max date to find max time on specific date
    date_file_names = [file for file in file_names if str(max_date) in file]

    # Use a list comprehension to extract the numeric part of each file name for time
    time = [int(file.split('T')[1].split('_')[0]) for file in date_file_names]
    time_sorted = np.sort(time)

    # Use search sorted to find max time below given time
    max_time = time_sorted[np.searchsorted(time_sorted, gli_time, side='right')-1]

    # Use another list comprehension to find the file name with the maximum value
    max_file = [file for file in file_names if str(max_date) in file and str(max_time) in file]

    return max_file

def prepare_data(gli_data,sci_data,conditions): 
#returns dataset of flight and science data sorted by time with sensor columns filled

    #open flight and science data using xarray and convert to pandas dataframe
    df_gli = xr.open_dataset(gli_data)
    df_sci = xr.open_dataset(sci_data)
    data_gli = df_gli.to_dataframe()
    data_sci = df_sci.to_dataframe()

    #combien flight and science and sort them by the time variable
    datafull = pd.concat([data_gli, data_sci], sort=True).sort_values(by='time')

    datafull.reset_index()

    #create empty list for sensor names
    sensor_names = []

    #parse conditions in cinditions input and append the sensor names to the list
    for condition in conditions:
        sensor, operator, value = condition.split(':')
        sensor_names.append(sensor)

    #use bfill and ffill to fill in missing sensor values with the last value before the empty space
    for sensor in sensor_names:
        datafull[sensor] = datafull[sensor].fillna(method='ffill')
        datafull[sensor] = datafull[sensor].fillna(method='bfill')

    datafull = datafull.reset_index()

    return datafull

def find_indices(data, conditions, time_name, datetime_range=[0,0,0,0]):
#finds indices in dataset where all conditions are met

    #check if user input a datetime
    if datetime_range != [0,0,0,0]:
        datetime_range_check = True
    else:
        datetime_range_check = False

    #create empty list for conditions and sensor names
    cond_list = []
    sensor_names = []

    #parse conditions and append conditional statements to cond_list
    for condition in conditions:
        sensor, operator, value = condition.split(':')
        sensor_names.append(sensor)
        if operator == '=':
            cond_list.append(data[sensor]==int(value))
        if operator == '<=':
            cond_list.append(data[sensor]<=int(value))
        if operator == '<':
            cond_list.append(data[sensor]<int(value))
        if operator == '>=':
            cond_list.append(data[sensor]>=int(value))
        if operator == '>':
            cond_list.append(data[sensor]>int(value))
        if operator == '!=':
            cond_list.append(data[sensor]!=int(value))

    #create mask and add each conditional statement to it with an &
    mask = cond_list[0]
    for expression in cond_list[1:]:
        mask = mask & expression

    #convert to numpy
    mask = mask.values

    #convert to int
    mask = mask.astype(int)

    #use np.diff within np.where to find indices where mask values changes from 1 to 0 for end or 0 to 1 for start
    start_indices = np.where(np.diff(mask) == 1)[0]
    end_indices = np.where(np.diff(mask) == -1)[0]

    if datetime_range_check:
        #define start and end time as datetime object based on datetime_range array
        startdt = datetime.datetime.strptime(datetime_range[0] + ' ' + datetime_range[1], "%Y%m%d %H%M%S")
        enddt = datetime.datetime.strptime(datetime_range[2] + ' ' + datetime_range[3], "%Y%m%d %H%M%S")

        #find start and end indices within old indices that conform to datetime range
        start_indices = [idx for idx in start_indices if data.loc[idx, time_name] > startdt and data.loc[idx, time_name] < enddt]
        end_indices = [idx for idx in end_indices if data.loc[idx, time_name] > startdt and data.loc[idx, time_name] < enddt]
        
        #insert -1 if start or end index is before or after start or end time respectively

        #if there are no start indices, insert -1 as start index
        if len(start_indices) == 0:
            start_indices = np.array(start_indices)
            start_indices = np.append(start_indices,-1)

        #if there are no end_indices, insert -1 as end index
        if len(end_indices) == 0:
            end_indices = np.array(end_indices)
            end_indices = np.append(end_indices,-1)

        #if the first start index is after the first end_index, insert -1 as start index
        if start_indices[0] > end_indices[0]:
            start_indices = np.insert(start_indices,0,-1)

        #if there are more end indixes that start indices, insert -1 as last end index
        if len(end_indices) < len(start_indices):
            end_indices = np.insert(end_indices,len(end_indices),-1)

    else:
        #repeat for no datetime range
        if start_indices.size == 0:
            start_indices = np.array(start_indices)
            start_indices = np.append(start_indices,-1)

        if end_indices.size == 0:
            end_indices = np.array(end_indices)
            end_indices = np.append(end_indices,-1)

        if start_indices[0] > end_indices[0]:
            start_indices = np.insert(start_indices,0,0)

        if len(end_indices) < len(start_indices):
            end_indices = np.insert(end_indices,len(end_indices),-1)

    return start_indices,end_indices

def find_on_values(data,start_index,time_name, audiodir_path):
#finds when condition is met and timestamp in respective audio file

    #datetime from time column in data for start_index
    gli_datetime = data.loc[start_index,time_name]
    #seperates datetime into date and time
    gli_date = int(gli_datetime.strftime('%Y%m%d'))
    gli_time = int(gli_datetime.strftime('%H%M%S'))

    #calls find_wav_file to find wavefile for date and time of start index
    wavfile = find_wav_file(audiodir_path, gli_date, gli_time)

    #split name of found wavefile into date and time
    wavdate = wavfile[0].split('T')[0]
    wavtime = wavfile[0].split('T')[1].split('_')[0]

    #creates datetime object from date and time found from wavefile
    wavdt = datetime.datetime.strptime(wavdate + ' ' + wavtime, "%Y%m%d %H%M%S")

    #subtracts the time of the index from the wavefile start time to find timestamp in minutes:seconds
    timestamp_start = gli_datetime - wavdt

    total_seconds_start = timestamp_start.total_seconds()

    num_days, seconds = divmod(total_seconds_start, 86400)

    timestamp_start = datetime.timedelta(seconds=seconds)

    return gli_datetime, wavfile, timestamp_start

def find_off_values(data,end_index,time_name,audiodir_path):
#finds when condition is unmet and timestamp in respective audio file

    #datetime from time column in data for end_index
    gli_datetime2 = data.loc[end_index,time_name]
    #seperates datetime into date and time
    gli_date2 = int(gli_datetime2.strftime('%Y%m%d'))
    gli_time2 = int(gli_datetime2.strftime('%H%M%S'))
    
    #calls find_wav_file to find wavefile for date and time of end index
    nxtwavfile = find_wav_file(audiodir_path, gli_date2, gli_time2)

    #split name of found wavefile into date and time
    nxtwavdate = nxtwavfile[0].split('T')[0]
    nxtwavtime = nxtwavfile[0].split('T')[1].split('_')[0]

    #creates datetime object from date and time found from wavefile
    nxtwavdt = datetime.datetime.strptime(nxtwavdate + ' ' + nxtwavtime, "%Y%m%d %H%M%S")

    #subtracts the time of the index from the wavefile start time to find timestamp in minutes:seconds
    timestamp_end = gli_datetime2 - nxtwavdt

    total_seconds_end = timestamp_end.total_seconds()

    num_days, seconds = divmod(total_seconds_end, 86400)

    timestamp_end = datetime.timedelta(seconds=seconds)

    return gli_datetime2, nxtwavfile, timestamp_end

def find_sensor_audio_time_txt(data,conditions, start_indices, end_indices, time_name, audiodir_path, txtdir_path, file_name):
#creates text file containing the time the condition is met, the audio file, timestamp in audio file, 
#and these three values for when the condition is unmet

    #creates empty list for sensor names
    sensor_names = []

    #populate sensor_name list based on given conditions
    for condition in conditions:
        sensor, operator, value = condition.split(':')
        sensor_names.append(sensor)

    #start a counter for everytime condition is met
    instance_ctr = 0

    #create a name string based on user input
    name_string = file_name + '.txt'

    #create textpath name based on function inputs
    txtpathname = os.path.join(txtdir_path,name_string)

    #open textfile
    with open(txtpathname, 'w') as file:

        #loop through the paired start and end indices
        for start_index, end_index in zip(start_indices, end_indices):

            #increment counter for every index pair
            instance_ctr += 1

            file.write(f'Condition met instance {instance_ctr}\n')

            if start_index == -1 and end_index == -1:
                file.write(f'Condition was never met within given range\n')
            elif start_index == 0 or (start_index == -1 and end_index != -1):
                file.write(f'Condition met before start time\n')
            else:    
                gli_datetime, wavfile, timestamp_start = find_on_values(data,start_index,time_name, audiodir_path)

                file.write(f'Condition met: {gli_datetime} UTC \n')
                file.write(f'Condition met in audio file: {wavfile[0]}\n')
                file.write(f'Start timestamp in audio file: {timestamp_start}\n')

            if end_index == -1 and start_index != -1:
                file.write(f'Condition unmet after end time\n')
            elif end_index != -1:
                gli_datetime2, nxtwavfile, timestamp_end = find_off_values(data,end_index,time_name, audiodir_path)
                    
                file.write(f'Condition unmet: {gli_datetime2} UTC \n')
                file.write(f'Condition unmet in audio file: {nxtwavfile[0]}\n')
                file.write(f'End timestamp in audio file: {timestamp_end}\n')
                file.write('\n') 

def find_sensor_audio_time_csv(data,conditions, start_indices, end_indices, time_name, audiodir_path, csvdir_path, file_name):
#creates csv file containing the time the condition is met, the audio file, timestamp in audio file, 
#and these three values for when the condition is unmet

    #create empty list for sensor names
    sensor_names = []

    #initialize instance counter
    instance_ctr = 0
    #populate with sensor names in input conditions
    for condition in conditions:
        sensor, operator, value = condition.split(':')
        sensor_names.append(sensor)
   
    #create name string for csv file based on user input
    name_string = file_name + '.csv'

    #create path name for csv file based on input
    csvpathname = os.path.join(csvdir_path,name_string)

    #initialize accompanying text file
    with open(csvpathname, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time condition met","On Audio File","On timestamp","Time condition unmet","Off Audio File","Off timestamp"])
        csv_data = []

        #add data to csv for index pairs
        for start_index, end_index in zip(start_indices, end_indices):

            csv_data.clear()

            instance_ctr+=1
            print(f"Working on condition met instance {instance_ctr}")

            if start_index == -1 and end_index == -1:
                print(f'Condition was never met within given range')
                csv_data.append(np.nan)
                csv_data.append(np.nan)
                csv_data.append(np.nan)
            elif start_index == 0 or start_index == -1:
                print(f"Condition met instance {instance_ctr} was before start time")
                csv_data.append(np.nan)
                csv_data.append(np.nan)
                csv_data.append(np.nan)
            else:
                gli_datetime, wavfile, timestamp_start = find_on_values(data,start_index,time_name, audiodir_path)
                csv_data.append(gli_datetime)
                csv_data.append(wavfile[0])
                csv_data.append(timestamp_start)

            if end_index == -1 and start_index != -1:
                print(f"Condition unmet instance {instance_ctr} was after end time")
                csv_data.append(np.nan)
                csv_data.append(np.nan)
                csv_data.append(np.nan)
            elif end_index == -1 and start_index == -1:
                return
            else:
                gli_datetime2, nxtwavfile, timestamp_end = find_off_values(data,end_index,time_name, audiodir_path)
                csv_data.append(gli_datetime2)
                csv_data.append(nxtwavfile[0])
                csv_data.append(timestamp_end)
              
            writer.writerows([csv_data])

    print("Done")
    print(f"Output files in {csvdir_path}")