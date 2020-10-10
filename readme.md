# YouTube-NT Dataset
This repo contains python scripts can be used to prepare high quality video clips.

## Prepare your videos
In our paper: [Hierarchical Autoregressive Modeling for Neural Video Compression](https://openreview.net/pdf?id=TK_6nNb_C7q), YouTube-NT contains videos downloaded from the following YouTube Channels:

* [FRESH Movie Trailers](https://www.youtube.com/user/FilmsActuTrailers)
* [National Geographic](https://www.youtube.com/c/NatGeo)

As training a learned compression model usually requires high quality training data, we only download high quality videos by executing following command (Please install [youtube-dl](https://github.com/ytdl-org/youtube-dl) first):

* `youtube-dl -f bestvideo[ext=webm][height>=1080] -ciw -o "%(id)s.%(ext)s" -v <url-of-channel>`

Here, I recommend to download "webm" format videos as they are usually encoded with Google's VP9 codec, which usually has good quality and "ffmpeg" supports VP9 decode. Note that if you use "ext=mp4" you may download video with AV1 codec (really new), which may not be supported by some "ffmpeg" binary/package distribution (Of course, you can compile your own "ffmpeg" if you want). In addition, most mp4 files downloaded from youtube are encoded with H.264 codec, which usually has worse quality than VP9. For more details, please refer to [youtube-dl](https://github.com/ytdl-org/youtube-dl).

Of course, you can use your own videos.

## Use the scripts
1. Install `opencv-python` `ffmpeg` first.
2. `cd PySceneDetect; python setup.py install` # as I use a modified version of [PySceneDetect](https://pyscenedetect.readthedocs.io/projects/Manual/en/stable/)

3. Then we need to customize some values in [config.py](config.py) to detect scene cut and then extract each scene clip:
* `start = '15s'` # detection start time
* `duration = '120s'` # duration of detection
* `input_dir = 'videos'` # input path, your video folder
* `output_dir = 'splitted'` # output path, each subfolder will contain a scene clip (a sequence of .png files)
* `grayscale_filter = False` # whether use grayscale detection (will slow down the detection speed, use it only when you have lots of grayscale video)
* `gray_threshold = 35` # for scene cut detection, simply use this default value
* `threshold = 26` # for scene cut detection, simply use this default value
* `nframes = 10` # number of frames in each clip. Each scene clip may have "nframes//2" ~ "nframes" frames.
* `ffmpeg_override = f'-vf scale=iw*2/3:ih*2/3 -vsync 0 -vframes {nframes}'` # ffmpeg command. Here we need to downsample the original video to remove compression artifact
* `n_process = 64` # number of process

4. Execute `python main.py` and wait.. (it depends on how many videos you have)
5. The scripts will generate a file "badlist.csv", which contains the names of subfolder containing bad scene clips. Feel free to remove all the subfolders showed in this file.
