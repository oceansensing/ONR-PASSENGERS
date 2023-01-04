How to use processaudio.py

This python script requires processed netcdf form data, conditions to be met, the time variable to be used ('time') is recommended,
an optional datetime range, and pathing information in order to return a .txt and .csv file with every time the condition is met, 
then unmet, along with the corresponding audio file and timestamp.

An example processing script is given in the "example" directory

Step 1:
Install dependencies

The dependencies are listed in the requirements.txt file and glideraudio.py

For conda users:
In order to create a new environment with the required dependencies, open a terminal, navigate to the findaudio directory, and enter

"conda env create -f glideraudio.yml"

Activate the environment with

"conda activate glideraudio"


Step 2:
Adjust script to required inputs

Within processaudio.py, the following variables represent:

a. gli_data is the path to the netcdf file of flight data of the glider (ensure the pathing format is correct for your OS)
b. sci_data is the path to the netcdf file of science data of the (ensure the pathing format is correct for your OS)

c. conditions is an array of string specifying which parameters you'd like to retrieve the audio for. Enter each condition in the
following format "variable_name:conditional_operator:value"

Ex. ['sci_water_temp:>:20','sci_water_temp:<:30']

d. time_name is the variable name for the time variable you'd like to use ('time' is recommended)

e. outdir_path is the path to where you would like the output text and csv file to go 

f. file_name is what you would like to name your output text and csv files WITHOUT the extension

g. audiodir_path is the path to the folder containing the raw loggerhead .wav files

h. datetime_range is an optional range of the datetimes analyzed for the conditions. If the full dataset is required, either
don't use the datetime_range argument in the function call or enter ['0','0','0','0,] for the datetime_range.

The datetime range format is as follows ['start_date YYYYMMDD','start_time HHMMSS','end_date YYYYMMDD','end_time HHMMSS']

Ex. ['20221105','205000','20221108','221300'] In this example, the function will look for audio between November 5, 2022 20:50:00 UTC
and November 8 2022, 22:13:00 UTC

Ensure that every variable is a string (has '' around it) except for conditions and datetime_range, which should be
arrays where every item within the array is a string.


Step 3:
Running processaudio.py

Ensure that processaudio.py is in the same directory as findaudioparams.py

Open a terminal, navigate to the directory containing processaudio.py and findaudioparams.py, enter

"python processaudio.py"

The terminal should read the condition met instance it is working on. It will read done when finished and show where the text and csv
output files are. 


Step 4:
Understanding the output files

The text file will give the instance of the condition being met, followed by the time the condition was met,
the audio file in which it was met, and the timestamp within the audio file. It will give these same 3 values 
for when the condition was no longer met. The file will also specify if the condition was met before the given start time or unmet after the given end time.

The csv file will give the same information, however, the first three variables of the first line will be nan if the condition 
was met before the start time. Likewise for the last three variables of the last line if the condition was unmet after the end time.