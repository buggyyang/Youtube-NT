
start = '15s'
duration = '120s'
input_dir = 'videos'
output_dir = 'splitted'
grayscale_filter = True
gray_threshold = 35
threshold = 26
nframes = 10
ffmpeg_override = f'-vf scale=iw*2/3:ih*2/3 -vsync 0 -vframes {nframes}'
n_process = 64
