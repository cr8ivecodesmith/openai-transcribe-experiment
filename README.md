OpenAI Transcribe
===

POC for using OpenAI's audio transcribe functionality


OS Requirements

- FFMpeg


## Setup

Create an `.env` file containing your OpenAI API keys.


## Usage Notes

If you have MP4 files, you can convert them first to MP3s with FFMpeg:

```sh
ffmpeg -i video.mp4 -q:a 0 -map a video_audio.mp3
```

Then start transcribing it with the tool:

```sh
python transcribe.py video_audio.mp3
```

If you want to download a video you can use:

Fish

```sh
yt-dlp --config-location (pwd) URL
```

Bash

```sh
yt-dlp --config-location $(pwd) URL
```
