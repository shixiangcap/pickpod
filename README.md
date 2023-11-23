# Pickpod


[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-informational.svg)]()
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]()

Integrated tools to transfer internet audio to text, extract unpopular views, and pick up podcasts for you.

**`Pickpod`** helps to build your private wiki efficiently.

This repository contains:

1. A `Python` package that can easily call specified tasks.

2. A `Streamlit` app that provides a web UI to manage your podcast library.

3. Several package usage examples of complete tasks for target audio.

Welcome to our commercial deployment: [Pickpod](https://pickpod.shixiangcap.com/welcome), implementation with `Java` and microservice architecture.

Compared to the personal open-source prototype in this repository, the commercial version provides powerful performance and stable services.


## Table of Contents

- [Background](#background)

- [Install](#install)

- [Usage](#usage)

- [Examples](#examples)

- [Related Efforts](#related-efforts)

- [Maintainers](#maintainers)

- [Contributing](#contributing)

- [License](#license)


## Background

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/13c8b7b3-f901-462b-9cb4-396009fa0148" width=100%/>

The goals for **`Pickpod`** are:

1. High-quality integration with [yt-dlp](https://github.com/yt-dlp/yt-dlp), [faster-whisper](https://github.com/guillaumekln/faster-whisper), and [pyannote-audio](https://github.com/pyannote/pyannote-audio), so that users can quickly obtain the text result of the corresponding audio transcription by simply inputting a link or a local file.

2. The convenient use of [LISTEN NOTES Podcast API](https://www.listennotes.com/api/docs/) and [Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api). After completing the necessary settings and making a task, **`Pickpod`** can get the list of podcasts the users are interested in regularly according to the specified release period. Thus, the transcription task can be completed in batch. Then, **`Pickpod`** can pick up podcasts based on the evaluation through the extracted keywords, summaries, views, or only the `LLM`. Users can reference and modify the recommendation according to the sorting results of podcasts.

3. Rapid deployment for local environments, so that when the user launches the project, all features are easily accessible in the browser.


## Install

Since [ffmpeg and ffprobe](https://www.ffmpeg.org/) are strongly recommended by [yt-dlp](https://github.com/yt-dlp/yt-dlp#strongly-recommended), it is necessary to install the `ffmpeg binary` within the system before installing **`Pickpod`**.

You can refer to the installation method provided by [pydub](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up), or go to the [ffmpeg download page](https://ffmpeg.org/download.html) and [ffmpeg compilation guide](http://trac.ffmpeg.org/wiki/CompilationGuide) for more.

Moreover, please see the note about `hugging face` access token fetching in [pyannote-audio](https://github.com/pyannote/pyannote-audio#tldr-) for more information on using [speaker-diarization](https://huggingface.co/pyannote/speaker-diarization).

If you need to filter the list of podcasts to be batch transcribed based on customized rules or use `LLM` to analyze the transcribed text, please refer to the `API` documentation provided by [Listen Notes](https://www.listennotes.com/api/pricing/) and [Anthropic](https://docs.anthropic.com/claude/reference/getting-started-with-the-api#accessing-the-api) to obtain the necessary `Access Keys`, respectively.

### ❗️Warning

Due to **`Pickpod`** strictly restricting the version of used `Python` packages, some packages may automatically solve conflicts and remove some of the packages that you have installed before. To avoid unnecessary conflicts or damage to your environment, we strongly recommend installing **`Pickpod`** in a brand new `Python` environment or a `Python` virtual environment.

### Python

You don't need this source code if you just want to use the package. Just run:

```sh
$ pip install --upgrade pickpod
```

If you want to modify the package, install from source with:

```sh
$ pip install ./pickpod
```

If you want to run the `Streamlit` app that provides a web UI, install from source with:

```sh
$ pip install -r ./pickpod/app/requirements.txt
$ # For Linux or Unix
$ streamlit run ./pickpod/app/Home.py --server.port 8051
$ # For Windows
$ python -m streamlit run ./pickpod/app/Home.py --server.port 8051
```

Then visit `http://127.0.0.1:8051` in your local browser.

### Installation in a typical environment

We chose [nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04](https://hub.docker.com/layers/nvidia/cuda/11.8.0-cudnn8-runtime-ubuntu22.04/images/sha256-b4c8cec91bd17d5b8dd42a2ef5fb104eb39d9203f889f0f3f17a5bf45f7bccc0) as a typical system environment to try to install **`Pickpod`**. The docker image has the following base configuration:

```sh
$ python3 -V

  Python 3.10.12


$ nvidia-smi

  Tue Aug 15 08:06:56 2023
  +-----------------------------------------------------------------------------+
    NVIDIA-SMI 525.105.17   Driver Version: 525.105.17   CUDA Version: 12.0     |
  |-------------------------------+----------------------+----------------------+
    GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
                                  |                      |               MIG M. |
  |===============================+======================+======================|
      0  NVIDIA GeForce ...  On   | 00000000:65:00.0 Off |                  N/A |
     0%   43C    P8    23W / 370W |   1481MiB / 24576MiB |      0%      Default |
                                  |                      |                  N/A |
  +-------------------------------+----------------------+----------------------+

  +-----------------------------------------------------------------------------+
    Processes:                                                                  |
     GPU   GI   CI        PID   Type   Process name                  GPU Memory |
           ID   ID                                                   Usage      |
  |=============================================================================|
  +-----------------------------------------------------------------------------+
```

First, we need to install `ffmpeg`, `python3-pip`, and other essential tools, then upgrade the software packages.

```sh
$ sudo apt-get -y install cmake libsndfile1 ffmpeg python3-pip
$ sudo apt update && apt upgrade -y
```

We can verify if `ffmpeg` is installed successfully in the following way:

```sh
$ ffmpeg -version

  ffmpeg version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2000-2021 the FFmpeg developers
  built with gcc 11 (Ubuntu 11.2.0-19ubuntu1)
  configuration: --prefix=/usr --extra-version=0ubuntu0.22.04.1 --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --arch=amd64 --enable-gpl --disable-stripping --enable-gnutls --enable-ladspa --enable-libaom --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio --enable-libcodec2 --enable-libdav1d --enable-libflite --enable-libfontconfig --enable-libfreetype --enable-libfribidi --enable-libgme --enable-libgsm --enable-libjack --enable-libmp3lame --enable-libmysofa --enable-libopenjpeg --enable-libopenmpt --enable-libopus --enable-libpulse --enable-librabbitmq --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libsrt --enable-libssh --enable-libtheora --enable-libtwolame --enable-libvidstab --enable-libvorbis --enable-libvpx --enable-libwebp --enable-libx265 --enable-libxml2 --enable-libxvid --enable-libzimg --enable-libzmq --enable-libzvbi --enable-lv2 --enable-omx --enable-openal --enable-opencl --enable-opengl --enable-sdl2 --enable-pocketsphinx --enable-librsvg --enable-libmfx --enable-libdc1394 --enable-libdrm --enable-libiec61883 --enable-chromaprint --enable-frei0r --enable-libx264 --enable-shared
  libavutil      56. 70.100 / 56. 70.100
  libavcodec     58.134.100 / 58.134.100
  libavformat    58. 76.100 / 58. 76.100
  libavdevice    58. 13.100 / 58. 13.100
  libavfilter     7.110.100 /  7.110.100
  libswscale      5.  9.100 /  5.  9.100
  libswresample   3.  9.100 /  3.  9.100
  libpostproc    55.  9.100 / 55.  9.100
```

After downloading the source code and running `setup.py`, we can import **`Pickpod`** in `Python`.

```sh
$ git clone https://github.com/shixiangcap/pickpod.git
$ pip install ./pickpod
```


## Usage

### Do internet **`Pickpod`** task

```python
from pickpod.config import TaskConfig
from pickpod.draft import AudioDraft
from pickpod.task import PickpodTask

HUGGING_FACE_KEY = "YOUR_HUGGING_FACE_KEY"

# For example: https://www.youtube.com/watch?v=xxxxxxxxxxx
audio_url = "YOUR_AUDIO_URL_ON_INTERNET"

# Set audio information
audio_draft = AudioDraft(audio_url=audio_url)
# Config pickpod task
task_config = TaskConfig(key_hugging_face=HUGGING_FACE_KEY, pipeline=True)
# Initial pickpod task
pickpod_task = PickpodTask(audio_draft, task_config)
# Start pickpod task
pickpod_task.pickpod_with_url()
# Print the result of pickpod task
print(pickpod_task.__dict__)
```

### Do local **`Pickpod`** task

```python
from pickpod.config import TaskConfig
from pickpod.draft import AudioDraft
from pickpod.task import PickpodTask

HUGGING_FACE_KEY = "YOUR_HUGGING_FACE_KEY"

# For example: xxxxxxxxxxx.m4a
audio_path = "YOUR_LOCAL_FILE_PATH"

# Set audio information
audio_draft = AudioDraft(audio_path=audio_path)
# Config pickpod task
task_config = TaskConfig(key_hugging_face=HUGGING_FACE_KEY, pipeline=False)
# Initial pickpod task
pickpod_task = PickpodTask(audio_draft, task_config)
# Start pickpod task
pickpod_task.pickpod_with_local()
# Save the result of pickpod task
pickpod_task.save_to_txt()
```


## Examples

### Modification of user configuration and task options

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/f4381862-c02a-4da4-ab94-84ecb1271115" width=100%/>

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/1b40c2e4-b0f3-4833-ac60-5183bc53208d" width=100%/>

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/776e803b-9546-4f84-8a6e-1df6dad39fc3" width=100%/>

### A **`Pickpod`** task returning results continuously during execution

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/2dd3f72f-d35c-489f-9733-1262c3b5dbba" width=100%/>

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/22cbb191-57a6-43ad-bb8b-1547411c5582" width=100%/>

### The operation of building and editing your private wiki

You can search podcasts in your `Gallery`.

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/d4c43b4e-1a48-45a0-a3fb-7282e825c3ed" width=100%/>

If you need **`Pickpod`** to pick up podcasts based on your private wiki, the prompt will use both valuable and worthless views.

<img src="https://github.com/shixiangcap/pickpod/assets/41248645/7b3c3ed0-1869-4d1c-9a48-7e6d1b016843" width=100%/>

### A complete transcription result of a audio file

If the target `YouTube` video is [Introducing GPT-4](https://www.youtube.com/watch?v=--khbXchTeE), the **`Pickpod`** can get the `JSON` file [afeb5810-25ee-426d-aa88-7b58484d4c6f.json](./examples/afeb5810-25ee-426d-aa88-7b58484d4c6f.json)

If the target `小宇宙` podcast is [EP 35. ICML现场对话AI研究员符尧：亲历AI诸神之战，解读LLM前沿研究，Llama 2，AI Agents](https://www.xiaoyuzhoufm.com/episode/64d0c50ae490c5dee5ca5721), the **`Pickpod`** can get the `JSON` file [93aa3140-300d-4af6-9d9c-2c41e9095821.json](./examples/93aa3140-300d-4af6-9d9c-2c41e9095821.json)


## Related Efforts

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - A youtube-dl fork with additional features and fixes.

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Faster Whisper transcription with CTranslate2.

- [pyannote-audio](https://github.com/pyannote/pyannote-audio) - Neural building blocks for speaker diarization: speech activity detection, speaker change detection, overlapped speech detection, speaker embedding.


## Maintainers

[@shixiangcap](https://github.com/shixiangcap)


## Contributing

Feel free to dive in! [Open an issue](https://github.com/shixiangcap/pickpod/issues/new) or submit PRs.


## License

[MIT](LICENSE) © shixiangcap
