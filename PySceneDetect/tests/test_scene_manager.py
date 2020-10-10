# -*- coding: utf-8 -*-
#
#         PySceneDetect: Python-Based Video Scene Detector
#   ---------------------------------------------------------------
#     [  Site: http://www.bcastell.com/projects/PySceneDetect/   ]
#     [  Github: https://github.com/Breakthrough/PySceneDetect/  ]
#     [  Documentation: http://pyscenedetect.readthedocs.org/    ]
#
# Copyright (C) 2014-2020 Brandon Castellano <http://www.bcastell.com>.
#
# PySceneDetect is licensed under the BSD 3-Clause License; see the included
# LICENSE file, or visit one of the following pages for details:
#  - https://github.com/Breakthrough/PySceneDetect/
#  - http://www.bcastell.com/projects/PySceneDetect/
#
# This software uses Numpy, OpenCV, click, tqdm, simpletable, and pytest.
# See the included LICENSE files or one of the above URLs for more information.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

""" PySceneDetect scenedetect.scene_manager Tests

This file includes unit tests for the scenedetect.scene_manager module (specifically,
the SceneManager object, used to coordinate using SceneDetector objects on video
capture/frame sources like the scenedetect.video_decoder.VideoManager object, or
a cv2.VideoCapture object).

In addition to the SceneManager class, these tests also require the PySceneDetect
FrameTimecode, VideoManager, and VideoManagerAsync objects, and the OpenCV
VideoCapture object.

These unit tests test the VideoManager object with respect to object construction,
testing argument format/limits, opening videos and grabbing frames, and appending
multiple videos together.

These tests rely on the testvideo.mp4 test video file, available by checking out the
PySceneDetect git repository "resources" branch, or the following URL to download it
directly:  https://github.com/Breakthrough/PySceneDetect/tree/resources/tests
Alternatively, the TEST_VIDEO_FILE constant can be replaced with any valid video file.
"""

# Standard project pylint disables for unit tests using pytest.
# pylint: disable=no-self-use, protected-access, multiple-statements, invalid-name
# pylint: disable=redefined-outer-name


# Third-Party Library Imports
import cv2

# PySceneDetect Library Imports
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.video_manager import VideoManager
from scenedetect.detectors import ContentDetector


def test_content_detect(test_video_file):
    """ Test SceneManager with VideoManager and ContentDetector. """
    vm = VideoManager([test_video_file])
    sm = SceneManager()
    sm.add_detector(ContentDetector())

    try:
        video_fps = vm.get_framerate()
        start_time = FrameTimecode('00:00:00', video_fps)
        end_time = FrameTimecode('00:00:05', video_fps)

        vm.set_duration(start_time=start_time, end_time=end_time)
        vm.set_downscale_factor()

        vm.start()
        num_frames = sm.detect_scenes(frame_source=vm)
        assert num_frames == end_time.get_frames() + 1

    finally:
        vm.release()


def test_content_detect_opencv_videocap(test_video_file):
    """ Test SceneManager with cv2.VideoCapture and ContentDetector. """
    cap = cv2.VideoCapture(test_video_file)
    sm = SceneManager()
    sm.add_detector(ContentDetector())

    try:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        duration = FrameTimecode('00:00:05', video_fps)

        num_frames = sm.detect_scenes(frame_source=cap, end_time=duration)

        assert num_frames == duration.get_frames()

    finally:
        cap.release()


def test_scene_list(test_video_file):
    """ Test SceneManager get_scene_list method with VideoManager/ContentDetector. """
    vm = VideoManager([test_video_file])
    sm = SceneManager()
    sm.add_detector(ContentDetector())

    try:
        base_timecode = vm.get_base_timecode()
        video_fps = vm.get_framerate()
        start_time = FrameTimecode('00:00:05', video_fps)
        end_time = FrameTimecode('00:00:15', video_fps)

        assert end_time.get_frames() > start_time.get_frames()

        vm.set_duration(start_time=start_time, end_time=end_time)
        vm.set_downscale_factor()

        vm.start()
        num_frames = sm.detect_scenes(frame_source=vm)

        assert num_frames == (1 + end_time.get_frames() - start_time.get_frames())

        scene_list = sm.get_scene_list(base_timecode)
        assert scene_list
        # Each scene is in the format (Start Timecode, End Timecode)
        assert len(scene_list[0]) == 2

        for i, _ in enumerate(scene_list):
            assert scene_list[i][0].get_frames() < scene_list[i][1].get_frames()
            if i > 0:
                # Ensure frame list is sorted (i.e. end time frame of
                # one scene is equal to the start time of the next).
                assert scene_list[i-1][1] == scene_list[i][0]

    finally:
        vm.release()
