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

## Transcript → Article

Generate a formatted article from a transcript using a prompt defined in `articles.toml`.

- Configure article types in `articles.toml` (each top-level table needs a `prompt` and can optionally set a `model`).
- Use `{transcript}` in the prompt to interpolate the transcript text.

Run:

```sh
python transcript_to_article.py <ARTICLE_TYPE> <PATH/TO/transcript.txt>
```

Output is written to `output/<transcript_stem>_<ARTICLE_TYPE>.md` by default, or use `-o/--output-dir` to choose a directory.

### Model Selection

You can choose which model generates each article type by setting `model` in `articles.toml`. If omitted, the script defaults to `gpt-4o-mini`.

Recommended options for article generation:

- gpt-4o: Highest quality and formatting fidelity. Great for polished blog posts, nuanced tone, and long transcripts.
- gpt-4.1: Strong reasoning and instruction following. Good for complex outlines and dense technical recaps.
- gpt-4o-mini: Fast and cost‑efficient. Ideal for meeting notes, summaries, and quick drafts.
- gpt-4.1-mini: Balanced quality/cost. Good for structured outlines and straightforward posts.

Tips:
- Use `gpt-4o` for final, publication-ready blog content.
- Use `gpt-4o-mini` for iterative drafting, notes, or when cost/latency matters.
- For long or messy transcripts, prefer `gpt-4o` or `gpt-4.1` to preserve nuance.

Example config per type (from `articles.toml`):

```toml
[blog]
model = "gpt-4o"
prompt = "..."

[notes]
model = "gpt-4o-mini"
prompt = "..."

[outline]
model = "gpt-4.1-mini"
prompt = "..."
```
