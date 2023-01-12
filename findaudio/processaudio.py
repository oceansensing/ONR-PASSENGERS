import findaudioparams as faud

datetime_range = ['20221105','205000','20221108','221300']
conditions = ['sci_water_temp:>:20','sci_water_temp:<:30']
time_name = 'time'
file_name = 'electa_20221105T20500-20221108T221300_20sci_water_temp30'

# glider data for electa can be downloaded from the links below:
# http://slocum-data.marine.rutgers.edu/erddap/tabledap/electa-20221105T1025-trajectory-raw-delayed.html
# http://slocum-data.marine.rutgers.edu/erddap/tabledap/electa-20221105T1025-profile-sci-delayed.html
gli_data = '/Users/jack/Downloads/electa-20221105T1025-trajectory-raw-delayed_0d79_ec66_3af8.nc'
sci_data = '/Users/jack/Downloads/electa-20221105T1025-profile-sci-delayed_2da9_5908_0ae3.nc'
audiodir_path = '/Users/jack/gliderData/electa-20221105-passengers-post/Loggerhead'
outdir_path = '/Users/jack/Documents/findaudio/output_files'

datafull = faud.prepare_data(gli_data,sci_data,conditions)

start_indices,end_indices = faud.find_indices(datafull,conditions, time_name,datetime_range)

faud.find_sensor_audio_time_txt(datafull, conditions, start_indices, end_indices, time_name, audiodir_path, outdir_path, file_name)
faud.find_sensor_audio_time_csv(datafull, conditions, start_indices, end_indices, time_name, audiodir_path, outdir_path, file_name)