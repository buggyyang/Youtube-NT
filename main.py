import os
import config
import multiprocessing
import subprocess
import cv2
import numpy as np


def compare(frame1, frame2):
    assert frame1.shape == frame2.shape
    num_pixels = frame1.shape[0] * frame1.shape[1]
    frame1_hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV).astype(np.int32)
    frame2_hsv = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV).astype(np.int32)
    delta_hsv = np.abs(frame1_hsv - frame2_hsv).sum(-1) / num_pixels
    delta_hsv_avg = delta_hsv.sum() / 3.
    return delta_hsv_avg


def compare_gray(frame1, frame2):
    assert frame1.shape == frame2.shape
    num_pixels = frame1.shape[0] * frame1.shape[1]
    frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY).astype(np.int32)
    frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY).astype(np.int32)
    delta_gray_avg = np.abs(frame1_gray - frame2_gray).sum() / num_pixels
    return delta_gray_avg


def process(fname):
    # print(f'processing {fname}')
    count, anchor = 0, -1
    folder = os.path.join(f'{config.output_dir}', fname)
    nframe = len(os.listdir(folder))
    for i in range(1, nframe):
        try:
            if i == 1:
                frame1 = cv2.imread(os.path.join(folder, f'{i}.png'))
                frame2 = cv2.imread(os.path.join(folder, f'{i+1}.png'))
            else:
                frame1 = frame2
                frame2 = cv2.imread(os.path.join(folder, f'{i+1}.png'))
            if (frame1.mean() < 5) or (frame1.mean() > 250) or (frame1.std() < 5) or (frame2.mean() < 5) or (
                    frame2.mean() > 250) or (frame2.std() < 5):
                return fname
            value = compare(frame1, frame2)
            if value > config.threshold:
                count += 1
                anchor = i
                if (count > 1):
                    return fname
            elif config.grayscale_filter:
                value = compare_gray(frame1, frame2)
                if value > config.gray_threshold:
                    count += 1
                    anchor = i
                    if (count > 1):
                        return fname
        except AttributeError:
            print(fname, 'has attribute error')
            return fname
    if (anchor <= config.nframes // 2) and (anchor != -1):
        for i in range(anchor + 1, 11):
            src = os.path.join(f'{config.output_dir}', fname, f'{i}.png')
            ftbo = os.path.join(f'{config.output_dir}', fname, f'{i - anchor}.png')
            if os.path.isfile(ftbo):
                os.remove(ftbo)
            os.rename(src, ftbo)
    elif (anchor > config.nframes // 2) and (anchor != -1):
        for i in range(anchor + 1, 11):
            os.remove(os.path.join(f'{config.output_dir}', fname, f'{i}.png'))
    return None


def split(fname):
    subprocess.call(f'{scenedetect} -i {config.input_dir}/{fname} \
            detect-content -t {config.threshold} \
                time -s {config.start} -d {config.duration} \
                    split-video -a "{config.ffmpeg_override}" -o {config.output_dir}',
                    shell=True)


flist = os.listdir(f'{config.input_dir}')
scenedetect = 'scenedetect'
if not os.path.isdir(f'{config.output_dir}'):
    os.mkdir(f'{config.output_dir}')

pool = multiprocessing.Pool(config.n_process)
pool.map(split, flist)

scenelist = os.listdir(f'{config.output_dir}')
# pool = multiprocessing.Pool()
bad_list = pool.map(process, scenelist)
bad_list = filter(lambda x: x is not None, bad_list)
np.savetxt('badlist.csv', list(bad_list), fmt="%s", delimiter=',')
