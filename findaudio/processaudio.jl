using PyCall, NCDatasets

datetime_range = ["20221105","205000","20221108","221300"]
conditions = ["sci_water_temp:>:20","sci_water_temp:<:30"]
time_name = "time"
file_name = "electa_test"

workdir = "/Users/gong/Research/electa-20221103-passengers/"; 
gli_data = workdir * "electa-20221105T1025-trajectory-raw-delayed_0d79_ec66_3af8.nc";
sci_data = workdir * "electa-20221105T1025-profile-sci-delayed_2da9_5908_0ae3.nc";
audiodir_path = "/Users/gong/oceansensing Dropbox/C2PO/glider/gliderData/electa-20221105-passengers-post/Loggerhead";
outdir_path = workdir * "findaudio_output_files";

pushfirst!(pyimport("sys")."path", workdir);
faud = pyimport("findaudioparams");

dsG = Dataset(gli_data,"r");
dsS = Dataset(sci_data,"r");


datafull = faud.prepare_data(gli_data,sci_data,conditions);

start_indices,end_indices = faud.find_indices(datafull,conditions, time_name,datetime_range);

faud.find_sensor_audio_time_txt(datafull, conditions, start_indices, end_indices, time_name, audiodir_path, outdir_path, file_name);
faud.find_sensor_audio_time_csv(datafull, conditions, start_indices, end_indices, time_name, audiodir_path, outdir_path, file_name);
